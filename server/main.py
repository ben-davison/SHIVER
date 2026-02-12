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

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# --- IMPORTS FOR TILING ---
from rio_tiler.io import Reader
from rio_tiler.errors import TileOutsideBounds
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import mercantile

# --- BACKEND FUNCTIONS --- 
from utils.extract_zarr_ts import get_glacier_timeseries

# --- CREDENTIALS ---
from dotenv import load_dotenv #
load_dotenv() # Load the variables from .env immediately

# --- CONFIGURATION: TIFF PATHS (ADDED) ---
current_os = platform.system()

if current_os == "Windows":
    base_path_gr = Path("R:/SCADI/output/Sentinel1/Greenland/mosaic/subregions/lev/multiyear/20141011_20250826")
    base_path_ant = Path("R:/SCADI/output/Sentinel1/Antarctica/mosaic/subregions/peninsula/multiyear/20141125_20250805")
else:
    base_path_gr = Path("/mnt/parscratch/users/gg1bjd/SCADI/output/Sentinel1/Greenland/mosaic/subregions/lev/multiyear/20141011_20250826")
    base_path_ant = Path("/mnt/parscratch/users/gg1bjd/SCADI/output/Sentinel1/Antarctica/mosaic/subregions/peninsula/multiyear/20141125_20250805")

TIFF_PATHS = {
    "Greenland": {
        "speed": base_path_gr / "S_median_20141011_20250826_200m_timefiltered_cog.tif",
        "u"    : base_path_gr / "U_median_20141011_20250826_200m_timefiltered_cog.tif",
        "v"    : base_path_gr / "V_median_20141011_20250826_200m_timefiltered_cog.tif",
        "count": base_path_gr / "perc_finite_px_20141011_20250826_200m_timefiltered_cog.tif",
        "trend": base_path_gr.parent / "speed_linear_trend_20141017_20251224_200m_raw_smoothed_spatial3x3_sig_masked.tif"
    },
    "Antarctica": {
        "speed": base_path_ant / "S_median_20141125_20250805_200m_timefiltered_cog_masked.tif",
        "u":     base_path_ant / "U_median_20141125_20250805_200m_timefiltered_cog_masked.tif",
        "v":     base_path_ant / "V_median_20141125_20250805_200m_timefiltered_cog_masked.tif",
        "count": base_path_ant / "perc_finite_px_20141125_20250805_200m_timefiltered_cog.tif",
        "trend": base_path_ant.parent / "speed_linear_trend_20141201_20251227_200m_raw_smoothed_spatial3x3_sig_masked.tif"
    }
}

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
        print(f"⚠️ Palette not found: {path}")
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
        print(f"✅ Loaded {len(palette_arr)} colors from {path.name}")
        return palette_arr

    except Exception as e:
        print(f"❌ Error loading palette {path.name}: {e}")
        return None

# Load Palettes
PALETTES = {}
for region, path in PALETTE_FILES.items():
    PALETTES[region] = load_custom_palette(path)
   
# Begin
app = FastAPI(
    title="Ice Velocity API",
    description="High-performance API for extracting glacier velocity time-series from Zarr.",
    version="1.0.0"
)

# --- CONFIG: CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",                 # Local Vue testing
        "https://ben-davison.github.io",         # Public Frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class LoginRequest(BaseModel):
    password: str

# --- ROUTES ---

@app.get("/health")
def health_check():
    """Simple check to see if server is running."""
    return {"status": "active", "engine": "FastAPI"}


# --- VECTOR TILE ENDPOINT ---
@app.get("/api/tiles/{region}/vectors/{z}/{x}/{y}.png")
async def get_vector_tile(region: str, z: int, x: int, y: int):
    try:
        if region not in TIFF_PATHS:
            raise HTTPException(status_code=404, detail=f"Region '{region}' not found")
        
        paths = TIFF_PATHS[region]

        # 1. Read Data
        try:
            with Reader(paths["u"]) as src_u: u_data = src_u.tile(x, y, z)
            with Reader(paths["v"]) as src_v: v_data = src_v.tile(x, y, z)
            with Reader(paths["speed"]) as src_s: s_data = src_s.tile(x, y, z)
        except TileOutsideBounds:
            return _empty_tile()

        # 2. Extract Arrays & Handle NaNs
        U = np.nan_to_num(u_data.data[0], nan=0.0)
        V = np.nan_to_num(v_data.data[0], nan=0.0)
        S = np.nan_to_num(s_data.data[0], nan=0.0)
        
        # 3. Filter Logic (Speed >= 20 and not 0)
        if region == "Greenland":
            valid_pixels = (S >= 20) & (S != 0) & (U != -9999) & (V != -9999)
        else:
            valid_pixels = (S >= 20) & (S != 0) & (U != -9999) & (V != -9999) & (S <= 3000) & (abs(U) <= 3000) & (abs(V) <= 3000)
        
        # 4. Decimate (16x16 grid)
        step = 16 
        h, w = U.shape
        
        # Create Pixel Grid (0 to 256)
        # We need the centers of the pixels for accurate rotation
        xs = np.arange(0, w, step) + step / 2
        ys = np.arange(0, h, step) + step / 2
        X, Y = np.meshgrid(xs, ys)
        
        # Subsample data
        U_sub = U[::step, ::step]
        V_sub = V[::step, ::step]
        mask_sub = valid_pixels[::step, ::step]

        if not np.any(mask_sub):
            return _empty_tile()

        # --- 5. ROTATION (Grid North -> True North) ---
        # Get the lat/lon bounds of this specific tile
        bounds = mercantile.bounds(x, y, z)
        
        # Generate Longitude grid for the decimated pixels
        # Linearly interpolate longitude from West to East edge of tile
        lons_row = np.linspace(bounds.west, bounds.east, U_sub.shape[1])
        # Broadcast to full grid (shape: 16x16)
        Lons = np.tile(lons_row, (U_sub.shape[0], 1))

        # Calculate Rotation Angle (Theta)
        # EPSG:3413 (Greenland) Central Meridian is -45 degrees
        # EPSG:3031 (Antarctica) Central Meridian is 0 degrees
        if region == "Greenland":
            central_meridian = -45.0
            theta = (Lons - central_meridian) * (np.pi / 180.0)
        else:
            central_meridian = 0.0
            theta = (Lons - central_meridian) * (np.pi / 180.0)

        # Apply Rotation
        # u_geo = u_grid * cos(theta) + v_grid * sin(theta)
        # v_geo = -u_grid * sin(theta) + v_grid * cos(theta)
        U_rot = U_sub * np.cos(theta) - V_sub * np.sin(theta)
        V_rot = V_sub * np.cos(theta) + U_sub * np.sin(theta)

        # 6. Masking
        U_masked = np.ma.masked_where(~mask_sub, U_rot)
        V_masked = np.ma.masked_where(~mask_sub, V_rot)

        # 7. Plotting
        dpi = 100
        fig = Figure(figsize=(2.56, 2.56), dpi=dpi, facecolor=(0,0,0,0))
        canvas = FigureCanvas(fig)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_axis_off() 
        ax.set_xlim(0, w)
        ax.set_ylim(h, 0) # Invert Y

        # STYLE SETTINGS
        # scale=2000: 2000 m/yr = 1 unit length. Adjust this number to change global arrow size.
        # width=0.010: Thinner shaft
        # headlength=3: Shorter head (reveals more tail)
        # headaxislength=2.5: Makes the back of the head less "swept back"
        if region == "Greenland":
            ax.quiver(X, Y, U_masked, V_masked, 
                      color='black', 
                      headlength=2, 
                      headaxislength=2.5, 
                      headwidth=3.0,
                      pivot='middle',
                      scale=2250,   
                      width=0.0075)  # Thinner arrows
        else:
            ax.quiver(X, Y, U_masked, V_masked, 
                      color='black', 
                      headlength=2, 
                      headaxislength=2.5, 
                      headwidth=3.0,
                      pivot='middle',
                      scale=5000,   
                      width=0.0075)  # Thinner arrows

        buf = io.BytesIO()
        canvas.print_png(buf)
        plt.close(fig)
        buf.seek(0)
        return Response(content=buf.read(), media_type="image/png")

    except Exception as e:
        print(f"🔥 Vector Error: {e}")
        return _empty_tile()

def _empty_tile():
    empty_img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    buf = io.BytesIO()
    empty_img.save(buf, format="PNG")
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")
        
        

# 2D overlays
@app.get("/api/tiles/{region}/{layer_type}/{z}/{x}/{y}.png")
async def tile(region: str, layer_type: str, z: int, x: int, y: int):
    """
    Dynamic Tile Server: Region-specific limits & Transparency rules.
    """
    if region not in TIFF_PATHS or layer_type not in TIFF_PATHS[region]:
        raise HTTPException(status_code=404, detail="Layer not found")
    
    file_path = TIFF_PATHS[region][layer_type]
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

    try:
        with Reader(file_path) as cog:
            try:
                img = cog.tile(x, y, z)
            except TileOutsideBounds:
                return Response(content=Image.new('RGBA', (256, 256), (0, 0, 0, 0)).tobytes("png"), media_type="image/png")

            data = img.data[0].astype('float32')

            alpha_mask = np.zeros(data.shape, dtype=np.uint8)
            
            # --- 1. MASK CREATION ---
            if layer_type == "speed":
                # --- SPEED LOGIC ---
                # Fast ice (> 20 m/yr) -> Solid Opaque
                alpha_mask[data >= 20] = 255
                
                # Slow/Stagnant ice (0-20 m/yr) -> Semi-transparent
                # This de-emphasizes noise in stable areas
                alpha_mask[(data > 0) & (data < 20)] = 60
                
            elif layer_type == "trend":
                 # Mask out NaNs or arbitrary nodata values (often -9999 or similar)
                 # Adjust this condition if your trend file uses specific nodata values
                alpha_mask[~np.isnan(data)] = 255
                
                # Make areas with a weak trend very transparent
                alpha_mask[(data > -0.5) & (data < 0.5)] = 40
                
            else:
                # --- COUNT LOGIC ---
                # For data density, we want to see everything that exists.
                # If we make low counts transparent, the deep purple of Viridis 
                # will vanish against the map background.
                alpha_mask[data > 0] = 255


            # --- 2. DATA PROCESSING ---
            if layer_type == "speed":
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
                if region == "Antarctica":
                    min_v, max_v = -15, 15
                else:
                    min_v, max_v = -2.5, 2.5

                norm = (data - min_v) / (max_v - min_v)
                use_custom = False # We will use matplotlib 'bwr'

            else:
                # Count Layer
                min_v, max_v = 0, 90
                norm = (data - min_v) / (max_v - min_v)
                use_custom = False

            norm = np.clip(norm, 0, 1)

            # --- 3. COLOR PAINTING ---
            height, width = data.shape
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
                    # 'bwr' = Blue-White-Red (0=Blue, 0.5=White, 1=Red)
                    # This matches the "positive = red" requirement
                    #cm_data = cm.bwr(norm) 
                    cm_data = cmc.vik(norm)
                else:
                    # 'viridis' for Count
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
        print(f"Tile Error: {e}")
        raise HTTPException(status_code=500, detail=f"Tile error: {str(e)}")
               
 
@app.post("/api/auth")
def authenticate(payload: LoginRequest):
    """
    Checks the password 
    """
    secret = os.getenv("SHIVER_PASSWORD")
    
    if not secret:
        # Fallback if you forgot to create the .env file
        print("⚠️ Warning: No password set in .env file")
        raise HTTPException(status_code=500, detail="Server misconfiguration")

    if payload.password == secret:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=401, detail="Incorrect password")

@app.post("/api/timeseries/json")
def extract_from_json(payload: RoiRequest):
    """
    Extracts time series for coordinates provided in JSON body.
    """
    print(f"JSON Request | Pts: {len(payload.roi)} | Buf: {payload.buffer} | Vars: {payload.variable} | Qual: {payload.quality}")
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
        print(f"❌ Error: {str(e)}")
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
    poly: int = Form(2)
):
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

if __name__ == "__main__":
    print("🚀 FastAPI Server starting on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_keep_alive=30)