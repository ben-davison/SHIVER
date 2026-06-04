import io
import numpy as np
import xarray as xr
import matplotlib
import cmcrameri.cm as cmc
import zarr
import math
from PIL import Image
from rio_tiler.io import Reader
from rio_tiler.models import ImageData
from rio_tiler.errors import TileOutsideBounds
from functools import lru_cache


# --- PRE-COMPUTE COLORMAP LUTS ---
def _create_lut(cmap_func):
    """Pre-computes a 256-color RGB Lookup Table."""
    return (cmap_func(np.linspace(0, 1, 256))[:, :3] * 255).astype(np.uint8)

LUTS = {
    "viridis": _create_lut(matplotlib.colormaps["viridis"]),
    "vik": _create_lut(cmc.vik),
    "batlow": _create_lut(cmc.batlow)
}


# --- CACHED ZARR LOADER ---
@lru_cache(maxsize=16)
def get_cached_zarr(zarr_path: str, group: str = "0"):
    """
    Opens a Zarr store with a chunk-level memory cache.
    Caches the actual uncompressed data chunks (up to 128MB).
    """
    # Pass the cached store into Xarray
    return xr.open_zarr(zarr_path, group=group, consolidated=True)



# --- APPLY COLORMAP ---
def apply_colormap(data_array, vmin, vmax, cmap_name="viridis"):
    """Normalizes a 2D numpy array and applies a pre-computed colormap, returning RGBA."""
    # 1. Handle NaN values (nodata)
    mask = np.isnan(data_array) | (data_array <= -9999) 
    
    # Sanitize data so array math and int casting don't crash on NaNs
    safe_data = np.copy(data_array)
    safe_data[mask] = vmin 
    
    # 2. Mathematical Normalization
    if cmap_name == "vik" and vmin < 0 < vmax:
        # Replicate TwoSlopeNorm: scale negatives 0.0 to 0.5, positives 0.5 to 1.0
        norm_data = np.where(
            safe_data < 0,
            0.5 * (safe_data - vmin) / (0.0 - vmin),
            0.5 + 0.5 * (safe_data - 0.0) / (vmax - 0.0)
        )
    else:
        # Standard linear normalization
        norm_data = (safe_data - vmin) / (vmax - vmin)
        
    # Strictly enforce 0.0 to 1.0 bounds
    norm_data = np.clip(norm_data, 0.0, 1.0)
    
    # 3. Map to 8-bit color indices (0-255)
    indices = (norm_data * 255).astype(np.int32)
    
    # 4. Build RGBA array
    height, width = data_array.shape
    rgba = np.zeros((height, width, 4), dtype=np.uint8)
    
    # Apply RGB channels via LUT indexing
    lut = LUTS.get(cmap_name, LUTS["viridis"])
    rgba[..., 0:3] = lut[indices]
    
    # 5. Apply Alpha Mask (Opaque by default, transparent for nodata)
    rgba[..., 3] = 255  
    rgba[mask, 3] = 0   
    
    return rgba


# --- FETCH COG ---
def fetch_cog_data(tif_path, bbox, width, height, target_crs="EPSG:4326"):
    """Reads a COG and returns the raw 2D numpy array resampled to width x height."""
    try:
        with Reader(tif_path) as src:
            # rio-tiler handles the bounding box crop and resampling perfectly
            img: ImageData = src.part(bbox, width=width, height=height, bounds_crs=target_crs)
            data = img.data[0].astype(float) # Grab the first band
            
            # Apply mask from rio-tiler if present (sets nodata to NaN)
            return np.where(img.mask[0] == 0, np.nan, data)
        
    except TileOutsideBounds:
        # 3. If Leaflet requests a tile completely off the map, return a block of NaNs
        return np.full((height, width), np.nan, dtype=float)


# --- FETCH ZARR ---
def fetch_zarr_data(zarr_path, bbox, width, height, epoch_idx, max_pyramid_level):
    """Extracts a 2D array from an OME-Zarr, using the optimal pyramid level."""
    xmin, ymin, xmax, ymax = bbox
    
    # 1. Calculate the WMS requested resolution (map units per pixel)
    req_res = abs(xmax - xmin) / width
    
    # 2. Get base resolution from the highest-detail group ("0")
    base_ds = get_cached_zarr(str(zarr_path), group="0")
    base_res = abs(float(base_ds.x[1].values - base_ds.x[0].values))
    
    # 3. Determine the optimal pyramid level
    if req_res > base_res * 2:
        level = int(math.log2(req_res / base_res))
        
        # Clamp to the maximum available pyramid level for this specific ice sheet
        level = min(level, max_pyramid_level)
        group_name = str(level)
    else:
        group_name = "0"

    # 4. Open the target dataset resolution
    ds = get_cached_zarr(str(zarr_path), group=group_name)
    
    # Create target coordinates 
    target_x = xr.DataArray(np.linspace(xmin, xmax, width), dims="x")
    target_y = xr.DataArray(np.linspace(ymax, ymin, height), dims="y")
    
    # Slice desired epoch
    single_epoch_data = ds['speed'].isel(time=int(epoch_idx))
    
    # Crop to bounding box to save memory
    y_slice = slice(ymax, ymin) if ds.y[0] > ds.y[-1] else slice(ymin, ymax)
    cropped = single_epoch_data.sel(x=slice(xmin, xmax), y=y_slice)
    
    try:
        subset = cropped.sel(x=target_x, y=target_y, method="nearest") 
        return subset.values
    except KeyError:
        return np.full((height, width), np.nan, dtype=float)


# --- RENDER ---
def render_array_to_png(data_array, vmin, vmax, cmap_name="viridis"):
    """Takes a raw 2D numpy array, applies colormaps, and converts it to a PNG."""
    rgba_img = apply_colormap(data_array, vmin, vmax, cmap_name)
    pil_img = Image.fromarray(rgba_img)
    
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return buf.getvalue()

