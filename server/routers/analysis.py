# server/routers/analysis.py
from fastapi import APIRouter, Request, HTTPException, Response
from utils.zarr_metadata import metadata_cache
from pathlib import Path
from utils.wms_renderer import fetch_cog_data, fetch_zarr_data, render_array_to_png
from config import ZARR_PATHS, COG_BASE_DIR
import traceback

router = APIRouter(
    prefix="/api/analysis",
    tags=["Analysis Map Layers"]
)

@router.get("/metadata/{region}")
async def get_zarr_metadata(region: str):
    """
    Returns the pre-cached list of available data sources and measurement epochs.
    """
    if region not in metadata_cache:
        raise HTTPException(status_code=404, detail=f"Metadata for region '{region}' not available.")
    
    return metadata_cache[region]


@router.get("/wms/{region}")
async def get_analysis_wms(region: str, req: Request):
    params = {k.lower(): v for k, v in req.query_params.items()}
    
    if params.get("request", "").lower() != "getmap":
        return Response("Only GetMap is supported", status_code=400)
        
    # Standard WMS BBOX (xmin, ymin, xmax, ymax)
    bbox_str = params.get("bbox")
    if not bbox_str:
        raise HTTPException(status_code=400, detail="Missing BBOX")
    bbox = tuple(map(float, bbox_str.split(",")))
    
    # Extract CRS from WMS request
    target_crs = params.get("crs", params.get("srs", "EPSG:4326")).upper()
    width = int(params.get("width", 256))
    height = int(params.get("height", 256))
    
    # Custom Vue Analysis Parameters
    variable = params.get("variable", "speed")
    source = params.get("source", "AllSources")
    epoch = params.get("epoch", "average")
    
    # New Compare Parameters
    compare_source = params.get("comparesource") 
    compare_epoch = params.get("compareepoch")
    
    vmin = float(params.get("vmin", 100))
    vmax = float(params.get("vmax", 3000))

    # --- HELPER FUNCTION ---
    def get_grid_data(src_name, ep):
        """Fetches data as a raw numpy array, abstracting COG vs Zarr logic."""
        file_src = "AllSources" if src_name == "all" else src_name
        
        # Determine if we need to load a COG or a Zarr
        if variable in ["trend", "count"] or ep == "average":
            var_suffix_map = {
                "trend": "Linear_Trend", 
                "count": "Epoch_Count", 
                "speed": "Mean_Speed"
            }
            suffix = var_suffix_map.get(variable, "Mean_Speed")
            filename = f"{region}_{file_src}_{suffix}.tif"
            tif_path = COG_BASE_DIR[region] / filename
            
            if not tif_path.exists():
                raise HTTPException(status_code=404, detail=f"COG not found: {filename}")
            
            return fetch_cog_data(str(tif_path), bbox, width, height, target_crs)
            
        else:
            zarr_path = ZARR_PATHS.get(region)
            if not zarr_path or not zarr_path.exists():
                raise HTTPException(status_code=404, detail="Zarr store not found.")
                
            return fetch_zarr_data(zarr_path, bbox, width, height, ep)
    # -----------------------

    try:
        # 1. Fetch Measurement Data
        data = get_grid_data(source, epoch)

        # 2. Fetch Reference Data & Calculate Difference (If requested)
        if compare_source and compare_epoch:
            ref_data = get_grid_data(compare_source, compare_epoch)
            # Subtract the two perfectly matching 2D numpy arrays
            data = data - ref_data

        # 3. Determine Colormap & Render
        is_difference = bool(compare_source and compare_epoch)
        if variable == "count":
            cmap = "viridis"
        elif variable == "trend" or is_difference:
            cmap = "vik"
        else:
            cmap = "batlow"
        
        png_bytes = render_array_to_png(data, vmin, vmax, cmap)
        
        return Response(content=png_bytes, media_type="image/png")

    except Exception as e:
        print("=== FULL TRACEBACK ===")
        traceback.print_exc()
        print("======================")
        raise HTTPException(status_code=500, detail=str(e))