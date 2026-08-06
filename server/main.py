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
import traceback
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
from routers import auth, multiSourceCube, users, analysis
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
    

# --- GLOBAL LOOKUP TABLES ---
def _create_lut(cmap_func):
    """Pre-computes a 256-color RGB Lookup Table from a Matplotlib colormap."""
    # Generate 256 values from 0 to 1, map them, drop alpha, and convert to uint8
    return (cmap_func(np.linspace(0, 1, 256))[:, :3] * 255).astype(np.uint8)

LUTS = {
    "trend": _create_lut(cmc.vik),
    "hillshade": _create_lut(cmc.grayC),
    "range": _create_lut(cm.magma),
    "default": _create_lut(cm.viridis)
}

   
# --- Begin ---
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
app.include_router(multiSourceCube.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(analysis.router)

# --- CONFIG: STATIC FILES ---
current_os = platform.system()
is_wsl = "WSL_DISTRO_NAME" in os.environ

if current_os == "Windows" or is_wsl:
    export_dir = current_dir / "static" / "exports"
else:
    export_dir = Path("/mnt/grio1/Shared/SHIVER/data/exports")

# Ensure the export directory exists
export_dir.mkdir(parents=True, exist_ok=True)

# 2. Mount the highly specific exports path FIRST
app.mount("/static/exports", StaticFiles(directory=export_dir), name="exports")

# 3. Mount the general static folder SECOND
static_path = current_dir / "static"
static_path.mkdir(exist_ok=True) 
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
def get_wms_vector(region: str, req: Request):
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

        # 2. DECIMATE FIRST (16x16 grid)
        # Slicing the raw arrays before doing any math saves ~99% of CPU cycles
        step = 16
        U_sub = u_img.data[0][::step, ::step]
        V_sub = v_img.data[0][::step, ::step]
        
        h, w = U_sub.shape # Note: This is now the small dimension (e.g., 16x16)

        # 3. Extract Arrays & Handle NaNs on the tiny arrays
        U_sub = np.nan_to_num(U_sub, nan=0.0)
        V_sub = np.nan_to_num(V_sub, nan=0.0)
        
        # Calculate dynamic speed (magnitude) using hypotenuse
        S_sub = np.hypot(U_sub, V_sub)
        
        # 4. Filter Logic
        valid_pixels = (S_sub >= 20) & (U_sub != -9999) & (V_sub != -9999)
        
        if not np.any(valid_pixels):
            return _empty_wms(width, height)

        # --- MAGNITUDE CAPPING ---
        max_speed = 1000.0
        cap_mask = S_sub > max_speed
        
        # Scale U and V down proportionately where the speed exceeds max_speed
        if np.any(cap_mask):
            scale_factor = max_speed / S_sub[cap_mask]
            U_sub[cap_mask] = U_sub[cap_mask] * scale_factor
            V_sub[cap_mask] = V_sub[cap_mask] * scale_factor

        # --- NO ROTATION NEEDED ---
        U_masked = np.ma.masked_where(~valid_pixels, U_sub)
        V_masked = np.ma.masked_where(~valid_pixels, V_sub)

        # 5. Plotting
        # Create Pixel Grid using the dynamic width/height
        # We base the grid on the original requested width/height, stepping by 16
        xs = np.arange(0, width, step) + step / 2
        ys = np.arange(0, height, step) + step / 2
        X, Y = np.meshgrid(xs, ys)

        dpi = 100
        fig = Figure(figsize=(width/dpi, height/dpi), dpi=dpi, facecolor=(0,0,0,0))
        canvas = FigureCanvas(fig)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_axis_off() 
        ax.set_xlim(0, width)
        ax.set_ylim(height, 0) # Invert Y for Matplotlib

        ax.quiver(X, Y, U_masked, V_masked, 
                  color='black', headlength=2, headaxislength=2.5, headwidth=3.0,
                  pivot='middle', scale=5000, width=0.0075) 

        buf = io.BytesIO()
        canvas.print_png(buf)
        plt.close(fig)
        buf.seek(0)
        tile_headers = {"Cache-Control": "public, max-age=86400, stale-while-revalidate=3600"} # 24 hours of caching (86400 seconds)
        return Response(content=buf.read(), media_type="image/png", headers=tile_headers)

    except Exception as e:
        print(f"Vector WMS Error: {e}")
        return _empty_wms(width, height)


# 2D overlays - WMS Polar Projections
@app.get("/api/wms/{region}")
def get_wms_overlay(region: str, req: Request):
    """
    Dynamic WMS Server for Polar Projections: Region-specific limits & Transparency rules.
    Accepts standard WMS parameters (BBOX, WIDTH, HEIGHT, CRS, LAYERS).
    """    
    # 1. Parse WMS Query Parameters (case-insensitive)
    params = {k.lower(): v for k, v in req.query_params.items()}
    
    if params.get("request", "").lower() != "getmap":
        return Response("Only GetMap is supported", status_code=400)

    layer_type = params.get("layers", "count")
    bbox_str = params.get("bbox")
    width = int(params.get("width", 256))
    height = int(params.get("height", 256))
    target_crs = params.get("crs", params.get("srs", "EPSG:4326"))
    
    nodata_val = 0 if layer_type in ["landsat_mosaic", "default_speed"] else None
    read_indexes = (1, 2, 3) if layer_type in ["landsat_mosaic", "default_speed"] else None

    if not bbox_str:
        return Response("Missing BBOX", status_code=400)

    minx, miny, maxx, maxy = map(float, bbox_str.split(","))
    
    # 2. Check Dictionary Lookups
    if region not in TIFF_PATHS:
        raise HTTPException(status_code=404, detail=f"Region '{region}' not configured")
        
    if layer_type not in TIFF_PATHS[region]:
        raise HTTPException(status_code=404, detail=f"Layer '{layer_type}' not found")

    # 3. Check File Path
    file_path = TIFF_PATHS[region][layer_type]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found on server at: {file_path}")
    
    try:
        with Reader(file_path) as cog:
            try:
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
                return _empty_wms(width, height)

            if layer_type == "landsat_mosaic":
                if img.data.dtype == 'float32' or img.data.dtype == np.float32:
                    data_max = np.nanmax(img.data)
                    
                    # 1. Normalize data
                    norm_data = np.clip(img.data if data_max <= 2.0 else img.data / 4000.0, 0.0, 1.0)
                    
                    # 2. Apply Gamma Stretch
                    gamma = 2.0 if region == "Greenland" else 1.2 
                    stretched_data = norm_data ** (1.0 / gamma) # ** is faster than np.power
                    
                    # 3. Convert to 8-bit RGB array
                    stretched_8bit = (stretched_data * 255).astype(np.uint8)
                    rgb_array = np.transpose(stretched_8bit, (1, 2, 0))
                    
                    # 4. Create the Alpha Mask & Assemble
                    alpha_mask = (np.sum(img.data, axis=0) > 0).astype(np.uint8) * 255
                    rgba_image = np.zeros((height, width, 4), dtype=np.uint8)
                    rgba_image[..., 0:3] = rgb_array
                    rgba_image[..., 3] = alpha_mask 
                    
                    buf = io.BytesIO()
                    Image.fromarray(rgba_image).save(buf, format="PNG")
                    tile_headers = {"Cache-Control": "public, max-age=86400, stale-while-revalidate=3600"}
                    return Response(content=buf.getvalue(), media_type="image/png", headers=tile_headers)
                    
                else:
                    tile_headers = {"Cache-Control": "public, max-age=86400, stale-while-revalidate=3600"}
                    return Response(content=img.render(img_format="PNG", nodata=0), media_type="image/png", headers=tile_headers)

            # --- PRECOLOURED SPEED OVERVIEW --- 
            if layer_type == "default_speed":
                tile_headers = {"Cache-Control": "public, max-age=86400, stale-while-revalidate=3600"}
                return Response(content=img.render(img_format="PNG", nodata=0), media_type="image/png", headers=tile_headers)
            
            # --- HILLSHADE --- #
            data = img.data[0].astype('uint8') if layer_type == "hillshade" else img.data[0].astype('float32')
            
            # Prevent NaN errors in mathematical operations
            data = np.nan_to_num(data, nan=0.0)

            alpha_mask = np.zeros(data.shape, dtype=np.uint8)
            
            # --- 1. MASK CREATION ---
            if layer_type == "speed":
                alpha_mask[data >= 20] = 255
                alpha_mask[(data > 0) & (data < 20)] = 60
            elif layer_type == "trend":
                alpha_mask[data != 0] = 255 # Handled NaNs above
                alpha_mask[(data > -0.5) & (data < 0.5)] = 40
            else:
                alpha_mask[data > 0] = 255

            # --- 2. DATA PROCESSING ---
            if layer_type == "dynamic_speed":
                max_v = 2000.0 if region == "Antarctica" else 400.0
                min_v = 1.0   
                
                log_min = np.log10(min_v)
                log_max = np.log10(max_v)

                # np.clip is heavily optimized in C compared to np.where
                safe_data = np.clip(data, min_v, None)
                norm = (np.log10(safe_data) - log_min) / (log_max - log_min)
                use_custom = True
                
            elif layer_type == "trend":
                min_v, max_v = -15, 15
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
                max_v = 200 if region == "Antarctica" else 750
                norm = data / max_v
                use_custom = False

            # Clip norm strictly between 0 and 1 so LUT indexing doesn't crash
            norm = np.clip(norm, 0, 1)

            # --- 3. COLOR PAINTING (LUT Optimization) ---
            rgba_image = np.zeros((height, width, 4), dtype=np.uint8)
            
            # Map 0.0-1.0 array to 0-255 integer indices
            indices = (norm * 255).astype(np.int32)

            if use_custom:
                current_palette = PALETTES.get(region, PALETTES.get("Greenland"))
                if current_palette is not None and len(current_palette) > 0:
                    pal_indices = (norm * (len(current_palette) - 1)).astype(np.int32)
                    rgba_image[..., 0:3] = current_palette[pal_indices]
                else:
                    # Grey Fallback using broadcasting
                    idx_byte = indices.astype(np.uint8)
                    rgba_image[..., 0:3] = np.stack([idx_byte]*3, axis=-1)
            else:
                # Direct lookup mapping - entirely bypassing Matplotlib!
                if layer_type == "trend":
                    rgba_image[..., 0:3] = LUTS["trend"][indices]
                elif layer_type == "hillshade":
                    rgba_image[..., 0:3] = LUTS["hillshade"][indices]
                elif layer_type == "range":
                    rgba_image[..., 0:3] = LUTS["range"][indices]
                else:
                    rgba_image[..., 0:3] = LUTS["default"][indices]

            # --- 4. APPLY MASK ---
            rgba_image[..., 3] = alpha_mask

            # 5. Save
            buf = io.BytesIO()
            Image.fromarray(rgba_image).save(buf, format="PNG")
            tile_headers = {"Cache-Control": "public, max-age=86400, stale-while-revalidate=3600"} # 24 hours of caching (86400 seconds)
            return Response(content=buf.getvalue(), media_type="image/png", headers=tile_headers)
            
    except Exception as e:
        print(f"WMS Tile Error: {e}")
        raise HTTPException(status_code=500, detail=f"WMS Tile error: {str(e)}")


# Helper function for transparent tiles
def _empty_wms(width: int, height: int):
    buf = io.BytesIO()
    Image.new('RGBA', (width, height), (0, 0, 0, 0)).save(buf, format="PNG")
    tile_headers = {"Cache-Control": "public, max-age=86400, stale-while-revalidate=3600"}
    return Response(content=buf.getvalue(), media_type="image/png", headers=tile_headers)


# Helper function for transparent tiles
def _empty_wms(width: int, height: int):
    buf = io.BytesIO()
    Image.new('RGBA', (width, height), (0, 0, 0, 0)).save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")

 
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
        
        # Handle top-level fatal errors from the utility (e.g., Zarr store unreadable)
        if "error" in results:
            error_msg = results["error"]
            # If the user sent bad input, throw a 400 Bad Request. Otherwise, throw a 500.
            status_code = 400 if "no geometries" in error_msg.lower() else 500
            raise HTTPException(status_code=status_code, detail=error_msg)

        # 
        return results
    
    except Exception as e:
        print(f"ERROR: Multi-source timeseries extraction error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An internal server error occurred during timeseries extraction.")
        


@app.post("/api/timeseries/upload")
def upload_shapefile(
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
def upload_multi_shapefile(
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