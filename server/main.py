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
from PIL import Image

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# --- NEW IMPORTS FOR TILING ---
from rio_tiler.io import Reader
from rio_tiler.errors import TileOutsideBounds

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
        "count": base_path_gr / "perc_finite_px_20141011_20250826_200m_timefiltered_cog.tif",
        "trend": base_path_gr.parent / "speed_linear_trend_20141017_20251224_200m_raw_smoothed_spatial3x3_sig_masked.tif"
    },
    "Antarctica": {
        "speed": base_path_ant / "S_median_20141125_20250805_200m_timefiltered_cog.tif",
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
    variables: List[str] = ["s"] # s, u, and/or v
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
                    max_v = 800.0
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
                    cm_data = cm.bwr(norm) 
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
    print(f"JSON Request | Pts: {len(payload.roi)} | Buf: {payload.buffer} | Vars: {payload.variables} | Qual: {payload.quality}")
    try:
        results = get_glacier_timeseries(
            location_input=payload.roi,
            buffer=payload.buffer,
            variables=payload.variables,
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
    variables: List[str] = Form(["s"]),
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
            variables=variables, 
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