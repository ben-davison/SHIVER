import sys
import os
from pathlib import Path
import shutil
import tempfile
import platform
from typing import List, Optional
import io
import numpy as np
import matplotlib.cm as cm
import cmcrameri.cm as cmc
from PIL import Image

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.responses import Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uvicorn

# --- IMPORTS FOR TILING ---
from rio_tiler.io import Reader
from rio_tiler.errors import TileOutsideBounds
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# --- BACKEND FUNCTIONS --- 
from utils.extract_zarr_ts import get_glacier_timeseries
from utils.extract_multi_zarr_ts import get_multi_glacier_timeseries
from utils.zarr_metadata import load_zarr_metadata, clear_zarr_metadata
import models
from routers import auth, cube, multiSourceCube, users, analysis
from models import get_db, User, DownloadLog
from dependencies import get_current_user_optional
from config import TIFF_PATHS


# --- CREDENTIALS ---
from dotenv import load_dotenv #
load_dotenv() # Load the variables from .env immediately

# --- LIFESPAN MANAGER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load the data into memory
    load_zarr_metadata()
    yield
    # Shutdown: Clear it out
    clear_zarr_metadata()


# Get the directory where main.py is located
current_dir = Path(__file__).resolve().parent

# --- 2. DYNAMIC PALETTE LOADING ---
PALETTE_DIR = current_dir / "palettes"
PALETTE_FILES = {
    "Greenland": PALETTE_DIR / "Greenland_palette.txt",
    "Antarctica": PALETTE_DIR / "Antarctica_palette.txt"
}

def load_custom_palette(path: Path):
    """
    Reads ALL lines from the text file. 
    Returns numpy array of shape (N, 3).
    """
    if not path.exists():
        print(f"Palette not found: {path}")
        return None

    colors = []
    try:
        with open(path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 3:
                    try:
                        r = int(float(parts[0]))
                        g = int(float(parts[1]))
                        b = int(float(parts[2]))
                        colors.append([r, g, b])
                    except ValueError:
                        continue
        
        # Convert to numpy array (N rows, 3 columns)
        palette_arr = np.array(colors, dtype=np.uint8)
        print(f"Loaded {len(palette_arr)} colors from {path.name}")
        return palette_arr

    except Exception as e:
        print(f"Error loading palette {path.name}: {e}")
        return None

# Load Palettes
PALETTES = {}
for region, path in PALETTE_FILES.items():
    PALETTES[region] = load_custom_palette(path)
   
# Begin
app = FastAPI(
    title="Ice Velocity API",
    description="High-performance API for extracting glacier velocity time-series from Zarr.",
    version="1.0.0",
    lifespan=lifespan
)

# --- CONFIG: CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",                 # Local Vue testing
        "http://localhost:5174",
        "http://localhost:8000",
        "http://127.0.0.1:5174",
        "https://ben-davison.github.io",         # Public Frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# Create the database tables in your dev environment
models.Base.metadata.create_all(bind=models.engine)

# --- Activate the new routes ---
app.include_router(cube.router)
app.include_router(multiSourceCube.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(analysis.router)

# --- CONFIG: STATIC FILES ---
# Mounts the 'static' folder to serve GeoJSON/CSS/JS files
static_path = current_dir / "static"
static_path.mkdir(exist_ok=True) # Creates it if it doesn't exist
app.mount("/static", StaticFiles(directory=static_path), name="static")

# --- DATA MODELS (Pydantic) ---
class RoiRequest(BaseModel):
    roi: List[List[float]]
    buffer: int = 500
    variable: List[str] = ["s"] # s, u, and/or v
    quality: List[str] = ["filt"] # filt and/or raw
    gap_fill: int = 24
    win_raw: int = 25
    win_daily: int = 25
    poly: int = 2
    
class MultiRoiRequest(BaseModel):
    roi: List[List[float]]
    buffer: int = 500
    sources: Optional[List[str]] = None
    gap_fill: int = 24
    win_raw: int = 25
    win_daily: int = 25
    poly: int = 2

class LoginRequest(BaseModel):
    password: str

# --- ROUTES ---

@app.get("/health")
def health_check():
    """Simple check to see if server is running."""
    return {"status": "active", "engine": "FastAPI"}



# --- VECTOR WMS ENDPOINT - POLAR PROJECTIONS ---
@app.get("/api/wms/{region}/vectors")
async def get_wms_vector(region: str, req: Request):
    """
    Dynamic WMS Server for Vector Overlays.
    No rotation required: The map and the data share the same polar stereographic grid!
    """
    params = {k.lower(): v for k, v in req.query_params.items()}
    
    if params.get("request", "").lower() != "getmap":
        return Response("Only GetMap is supported", status_code=400)

    bbox_str = params.get("bbox")
    width = int(params.get("width", 256))
    height = int(params.get("height", 256))
    target_crs = params.get("crs", params.get("srs", "EPSG:4326"))

    if not bbox_str:
        return Response("Missing BBOX", status_code=400)

    minx, miny, maxx, maxy = map(float, bbox_str.split(","))

    try:
        if region not in TIFF_PATHS:
            raise HTTPException(status_code=404, detail=f"Region '{region}' not found")
        
        paths = TIFF_PATHS[region]

        # 1. Read Data using .part() for the bounding box
        try:
            with Reader(paths["u"]) as src_u: 
                u_img = src_u.part(bbox=(minx, miny, maxx, maxy), bounds_crs=target_crs, dst_crs=target_crs, width=width, height=height)
            with Reader(paths["v"]) as src_v: 
                v_img = src_v.part(bbox=(minx, miny, maxx, maxy), bounds_crs=target_crs, dst_crs=target_crs, width=width, height=height)
        except TileOutsideBounds:
            return _empty_wms(width, height)

        # 2. Extract Arrays & Handle NaNs
        U = np.nan_to_num(u_img.data[0], nan=0.0)
        V = np.nan_to_num(v_img.data[0], nan=0.0)
        
        # Calculate dynamic speed (magnitude) using hypotenuse
        S = np.hypot(U, V)
        
        # 3. Filter Logic
        # Mask out completely empty pixels and very slow ice (< 20 m/yr) to declutter
        valid_pixels = (S >= 20) & (U != -9999) & (V != -9999)
        
        # --- MAGNITUDE CAPPING ---
        max_speed = 1000.0
        cap_mask = S > max_speed
        
        # Scale U and V down proportionately where the speed exceeds max_speed
        scale_factor = max_speed / S[cap_mask]
        U[cap_mask] = U[cap_mask] * scale_factor
        V[cap_mask] = V[cap_mask] * scale_factor
        
        # 4. Decimate (16x16 grid)
        step = 16
        h, w = U.shape
        
        # Create Pixel Grid using the dynamic width/height
        xs = np.arange(0, w, step) + step / 2
        ys = np.arange(0, h, step) + step / 2
        X, Y = np.meshgrid(xs, ys)
        
        # Subsample data
        U_sub = U[::step, ::step]
        V_sub = V[::step, ::step]
        mask_sub = valid_pixels[::step, ::step]

        if not np.any(mask_sub):
            return _empty_wms(width, height)

        # --- NO ROTATION NEEDED ---
        # The U and V components are naturally aligned with the map's grid.
        U_masked = np.ma.masked_where(~mask_sub, U_sub)
        V_masked = np.ma.masked_where(~mask_sub, V_sub)

        # 5. Plotting
        dpi = 100
        # Dynamically size the figure based on WMS request width/height
        fig = Figure(figsize=(width/dpi, height/dpi), dpi=dpi, facecolor=(0,0,0,0))
        canvas = FigureCanvas(fig)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_axis_off() 
        ax.set_xlim(0, w)
        ax.set_ylim(h, 0) # Invert Y for Matplotlib

        # You can now standardize the scale factor across both ice sheets if desired
        if region == "Greenland":
            ax.quiver(X, Y, U_masked, V_masked, 
                      color='black', headlength=2, headaxislength=2.5, headwidth=3.0,
                      pivot='middle', scale=5000, width=0.0075) 
        else:
            ax.quiver(X, Y, U_masked, V_masked, 
                      color='black', headlength=2, headaxislength=2.5, headwidth=3.0,
                      pivot='middle', scale=5000, width=0.0075) 

        buf = io.BytesIO()
        canvas.print_png(buf)
        plt.close(fig)
        buf.seek(0)
        return Response(content=buf.read(), media_type="image/png")

    except Exception as e:
        print(f"Vector WMS Error: {e}")
        return _empty_wms(width, height)

    except Exception as e:
        print(f"Vector WMS Error: {e}")
        return _empty_wms(width, height)

# Helper function for transparent tiles
def _empty_wms(width: int, height: int):
    empty_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    buf = io.BytesIO()
    empty_img.save(buf, format="PNG")
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")



# 2D overlays - WMS Polar Projections
@app.get("/api/wms/{region}")
async def get_wms_overlay(region: str, req: Request):
    """
    Dynamic WMS Server for Polar Projections: Region-specific limits & Transparency rules.
    Accepts standard WMS parameters (BBOX, WIDTH, HEIGHT, CRS, LAYERS).
    """    
    # 1. Parse WMS Query Parameters (case-insensitive)
    params = {k.lower(): v for k, v in req.query_params.items()}
    
    if params.get("request", "").lower() != "getmap":
        return Response("Only GetMap is supported", status_code=400)

    # In WMS, 'layers' tells us which variable to load (e.g., 'count', 'speed')
    layer_type = params.get("layers", "count")
    bbox_str = params.get("bbox")
    width = int(params.get("width", 256))
    height = int(params.get("height", 256))
    
    # Leaflet will pass EPSG:3413 (Greenland) or EPSG:3031 (Antarctica)
    target_crs = params.get("crs", params.get("srs", "EPSG:4326"))
    
    # Set defaults
    nodata_val = 0 if layer_type in ["landsat_mosaic", "default_speed"] else None
    read_indexes = (1, 2, 3) if layer_type in ["landsat_mosaic", "default_speed"] else None

    if not bbox_str:
        return Response("Missing BBOX", status_code=400)

    minx, miny, maxx, maxy = map(float, bbox_str.split(","))

    print(f"\n--- WMS REQUEST: {region} / {layer_type} ---")
    
    # 2. Check Dictionary Lookups
    if region not in TIFF_PATHS:
        print(f"Error: Region '{region}' not found in TIFF_PATHS keys: {list(TIFF_PATHS.keys())}")
        raise HTTPException(status_code=404, detail=f"Region '{region}' not configured")
        
    if layer_type not in TIFF_PATHS[region]:
        print(f"Error: Layer '{layer_type}' not found for region '{region}'. Available: {list(TIFF_PATHS[region].keys())}")
        raise HTTPException(status_code=404, detail=f"Layer '{layer_type}' not found")

    # 3. Check File Path
    file_path = TIFF_PATHS[region][layer_type]
    print(f"Looking for file at: {file_path}")
    print(f"   Absolute path: {file_path.absolute()}")

    if not file_path.exists():
        print(f"FILE MISSING! Python cannot see this file.")
        if str(file_path).startswith("R:"):
            print("   Note: You are using the R: drive. Ensure the terminal running Python has permissions to see it.")
        raise HTTPException(status_code=404, detail=f"File not found on server at: {file_path}")
    
    print("File found. Attempting to read bounding box...")

    try:
        with Reader(file_path) as cog:
            try:
                # Use .part() instead of .tile() for WMS bounding boxes
                img = cog.part(
                    bbox=(minx, miny, maxx, maxy),
                    bounds_crs=target_crs,
                    dst_crs=target_crs,
                    width=width,
                    height=height,
                    indexes=read_indexes,
                    nodata=nodata_val
                )
            except TileOutsideBounds:
                return Response(content=Image.new('RGBA', (width, height), (0, 0, 0, 0)).tobytes("png"), media_type="image/png")

            if layer_type == "landsat_mosaic":
                # Intercept the array to apply normalization and gamma stretch
                if img.data.dtype == 'float32' or img.data.dtype == np.float32:
                    data_max = np.nanmax(img.data)
                    
                    # 1. Normalize data to a 0.0 - 1.0 range 
                    if data_max <= 2.0:
                        norm_data = np.clip(img.data, 0.0, 1.0)
                    else:
                        norm_data = np.clip(img.data / 4000.0, 0.0, 1.0)
                    
                    # 2. Apply Gamma Stretch
                    gamma = 2.0 if region == "Greenland" else 1.2 
                    stretched_data = np.power(norm_data, 1.0 / gamma)
                    
                    # 3. Convert to 8-bit RGB array
                    stretched_8bit = (stretched_data * 255).astype(np.uint8)
                    rgb_array = np.transpose(stretched_8bit, (1, 2, 0))
                    
                    # 4. Create the Alpha Mask
                    alpha_mask = (np.sum(img.data, axis=0) > 0).astype(np.uint8) * 255
                    
                    # 5. Assemble final RGBA image
                    rgba_image = np.zeros((height, width, 4), dtype=np.uint8)
                    rgba_image[..., 0:3] = rgb_array
                    rgba_image[..., 3] = alpha_mask 
                    
                    # 6. Save and return using PIL
                    pil_img = Image.fromarray(rgba_image)
                    buf = io.BytesIO()
                    pil_img.save(buf, format="PNG")
                    return Response(content=buf.getvalue(), media_type="image/png")
                    
                else:
                    # Fallback for non-float data
                    rendered_img = img.render(img_format="PNG", nodata=0)
                    return Response(content=rendered_img, media_type="image/png")

            # --- PRECOLOURED SPEED OVERVIEW --- 
            if layer_type == "default_speed":
                # Render directly to PNG, forcing 0 as NoData so the background is transparent
                rendered_img = img.render(img_format="PNG", nodata=0)
                return Response(content=rendered_img, media_type="image/png")
            
            # --- HILLSHADE --- #
            if layer_type == "hillshade":
                data = img.data[0].astype('uint8')
            else:
                data = img.data[0].astype('float32')

            alpha_mask = np.zeros(data.shape, dtype=np.uint8)
            
            # --- 1. MASK CREATION ---
            if layer_type == "speed":
                # --- SPEED LOGIC ---
                # Fast ice (> 20 m/yr) -> Solid Opaque
                alpha_mask[data >= 20] = 255
                
                # Slow/Stagnant ice (0-20 m/yr) -> Semi-transparent
                alpha_mask[(data > 0) & (data < 20)] = 60
                
            elif layer_type == "trend":
                 # Mask out NaNs
                alpha_mask[~np.isnan(data)] = 255
                
                # Make areas with a weak trend very transparent
                alpha_mask[(data > -0.5) & (data < 0.5)] = 40
                
            elif layer_type == "hillshade":
                alpha_mask[data > 0] = 255
                
            elif layer_type == "range":
                alpha_mask[data > 0] = 255
                
            else:
                # --- COUNT LOGIC ---
                alpha_mask[data > 0] = 255


            # --- 2. DATA PROCESSING ---
            if layer_type == "dynamic_speed":
                # --- DYNAMIC LIMITS ---
                if region == "Antarctica":
                    max_v = 2000.0
                else:
                    max_v = 400.0 # Greenland default

                min_v = 1.0   
                
                # Log Scale Logic
                log_min = np.log10(min_v)
                log_max = np.log10(max_v)

                # Safe Log Calculation
                safe_data = np.where(data > min_v, data, min_v)
                log_data = np.log10(safe_data)
                norm = (log_data - log_min) / (log_max - log_min)
                use_custom = True
                
            elif layer_type == "trend":
                # --- TREND LOGIC ---
                # Diverging Scale: -10 to +10 m/yr^2
                min_v, max_v = -15, 15
                #if region == "Antarctica":
                #    min_v, max_v = -15, 15
                #else:
                #    min_v, max_v = -2.5, 2.5

                norm = (data - min_v) / (max_v - min_v)
                use_custom = False 
            
            elif layer_type == "hillshade":
                norm = data.astype(float) / 255.0
                use_custom = False
                
            elif layer_type == "range":
                min_v, max_v = 0, 50
                norm = (data - min_v) / (max_v - min_v)
                use_custom = False

            else:
                # Count Layer
                if region == "Antarctica":
                    min_v, max_v = 0, 200
                else:
                    min_v, max_v = 0, 750
                    
                norm = (data - min_v) / (max_v - min_v)
                use_custom = False

            norm = np.clip(norm, 0, 1)

            # --- 3. COLOR PAINTING ---
            rgba_image = np.zeros((height, width, 4), dtype=np.uint8)

            if use_custom:
                current_palette = PALETTES.get(region)
                if current_palette is None:
                    current_palette = PALETTES.get("Greenland")
                if current_palette is not None and len(current_palette) > 0:
                    num_colors = len(current_palette)
                    indices = (norm * (num_colors - 1)).astype(np.int32)
                    rgba_image[..., 0:3] = current_palette[indices]
                else:
                    # Grey Fallback
                    idx_byte = (norm * 255).astype(np.uint8)
                    rgba_image[..., 0] = idx_byte
                    rgba_image[..., 1] = idx_byte
                    rgba_image[..., 2] = idx_byte
            else:
                if layer_type == "trend":
                    cm_data = cmc.vik(norm)
                elif layer_type == "hillshade":
                    cm_data = cmc.grayC(norm)
                elif layer_type == "range":
                    cm_data = cm.magma(norm)
                else:
                    cm_data = cm.viridis(norm)
                
                # Convert to 0-255 uint8 and assign RGB channels
                rgba_image[..., 0] = (cm_data[..., 0] * 255).astype(np.uint8)
                rgba_image[..., 1] = (cm_data[..., 1] * 255).astype(np.uint8)
                rgba_image[..., 2] = (cm_data[..., 2] * 255).astype(np.uint8)

            # --- 4. APPLY MASK ---
            rgba_image[..., 3] = alpha_mask

            # 5. Save
            pil_img = Image.fromarray(rgba_image)
            buf = io.BytesIO()
            pil_img.save(buf, format="PNG")
            
            return Response(content=buf.getvalue(), media_type="image/png")
            
    except Exception as e:
        print(f"WMS Tile Error: {e}")
        raise HTTPException(status_code=500, detail=f"WMS Tile error: {str(e)}")


 
@app.post("/api/auth")
def authenticate(payload: LoginRequest):
    """
    Checks the password 
    """
    secret = os.getenv("SHIVER_PASSWORD")
    
    if not secret:
        # Fallback if you forgot to create the .env file
        print("Warning: No password set in .env file")
        raise HTTPException(status_code=500, detail="Server misconfiguration")

    if payload.password == secret:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=401, detail="Incorrect password")


@app.post("/api/timeseries/json")
def extract_from_json(
    payload: RoiRequest,
    # logging dependencies
    db: Session = Depends(get_db), 
    user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Extracts time series for coordinates provided in JSON body.
    """
    print(f"JSON Request | Pts: {len(payload.roi)} | Buf: {payload.buffer} | Vars: {payload.variable} | Qual: {payload.quality}")
    
    # --- LOGGING LOGIC ---
    if user:
        try:
            # Create a label (e.g. "Map Selection (1 points)")
            count = len(payload.roi)
            log_name = f"Map Selection ({count} points)"
            
            # Create the log entry
            log = DownloadLog(
                user_id=user.id,
                interaction_type="map_click",
                filename=log_name,
                file_size_mb=0.005 * count # Small estimate (5KB per point)
            )
            db.add(log)
            db.commit()
        except Exception as e:
            # We wrap this in try/except so logging errors don't break the actual data fetch
            print(f"Logging failed: {e}")
    
    try:
        results = get_glacier_timeseries(
            location_input=payload.roi,
            buffer=payload.buffer,
            variable=payload.variable,
            quality=payload.quality,
            # Pass new params
            gap_fill=payload.gap_fill,
            win_raw=payload.win_raw,
            win_daily=payload.win_daily,
            poly=payload.poly
        )
        return results
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        
        

@app.post("/api/timeseries/multi/json")
def extract_multi_from_json(
    payload: MultiRoiRequest,
    db: Session = Depends(get_db), 
    user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Extracts time series from the multi-source Zarr store for coordinates provided in JSON body.
    """
    print(f"Multi-Source JSON Request | Pts: {len(payload.roi)} | Buf: {payload.buffer}")
    
    # --- LOGGING LOGIC ---
    if user:
        try:
            count = len(payload.roi)
            log_name = f"Multi-Source Map Selection ({count} points)"
            
            log = DownloadLog(
                user_id=user.id,
                interaction_type="map_click_multi", # Differentiated interaction type
                filename=log_name,
                file_size_mb=0.005 * count 
            )
            db.add(log)
            db.commit()
        except Exception as e:
            print(f"Logging failed: {e}")
    
    try:
        # We will build this utility function next
        results = get_multi_glacier_timeseries(
            location_input=payload.roi,
            buffer=payload.buffer,
            sources=payload.sources,
            gap_fill=payload.gap_fill,
            win_raw=payload.win_raw,
            win_daily=payload.win_daily,
            poly=payload.poly
        )
        return results
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        


@app.post("/api/timeseries/upload")
async def upload_shapefile(
    file: UploadFile = File(...), 
    buffer: float = Form(500),
    variable: List[str] = Form(["s"]),
    quality: List[str] = Form(["filt"]),
    # New Form params
    gap_fill: int = Form(24),
    win_raw: int = Form(25),
    win_daily: int = Form(25),
    poly: int = Form(2),
    # logging dependencies
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    
    # 1. LOGGING LOGIC
    if user:
        try:
            # Estimate file size (file.size might be unavailable in spool, so we guess 0.5MB or check)
            # Or use: file.file.seek(0, 2); size = file.file.tell(); file.file.seek(0)
            size_mb = 0.5 
            
            log = DownloadLog(
                user_id=user.id,
                interaction_type="file_upload",
                filename=file.filename,
                file_size_mb=size_mb
            )
            db.add(log)
            db.commit()
        except Exception as e:
            print(f"Logging failed: {e}")
            
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        print(f"File Upload: {tmp_path} | Buf: {buffer}")
        results = get_glacier_timeseries(
            tmp_path, 
            buffer=buffer, 
            variable=variable, 
            quality=quality,
            gap_fill=gap_fill, win_raw=win_raw, win_daily=win_daily, poly=poly
        )
        return results
    except Exception as e:
        print(f"Error processing file: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if os.path.exists(tmp_path):
            try: os.remove(tmp_path)
            except PermissionError: pass
        

@app.post("/api/timeseries/multi/upload")
async def upload_multi_shapefile(
    file: UploadFile = File(...), 
    buffer: float = Form(500),
    sources: List[str] = Form([]), 
    gap_fill: int = Form(24),
    win_raw: int = Form(25),
    win_daily: int = Form(25),
    poly: int = Form(2),
    # logging dependencies
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    
    # 1. LOGGING LOGIC
    if user:
        try:
            size_mb = 0.5 
            
            log = DownloadLog(
                user_id=user.id,
                interaction_type="file_upload_multi", # Differentiated interaction type
                filename=file.filename,
                file_size_mb=size_mb
            )
            db.add(log)
            db.commit()
        except Exception as e:
            print(f"Logging failed: {e}")
            
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        print(f"Multi-Source File Upload: {tmp_path} | Buf: {buffer} | Sources: {sources}")
        
        # Call the multi-source extraction function instead of the single-source one!
        results = get_multi_glacier_timeseries(
            location_input=tmp_path, 
            buffer=buffer, 
            sources=sources, 
            gap_fill=gap_fill, 
            win_raw=win_raw, 
            win_daily=win_daily, 
            poly=poly
        )
        return results
    except Exception as e:
        print(f"Error processing multi-source file: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if os.path.exists(tmp_path):
            try: os.remove(tmp_path)
            except PermissionError: pass

if __name__ == "__main__":
    print("FastAPI Server starting on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_keep_alive=30)