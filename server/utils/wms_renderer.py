import io
import numpy as np
import xarray as xr
from PIL import Image
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import cmcrameri.cm as cmc
from rio_tiler.io import Reader
from rio_tiler.models import ImageData
from rio_tiler.errors import TileOutsideBounds
from functools import lru_cache

# 1. Create a cached loader function
@lru_cache(maxsize=4)
def get_cached_zarr(zarr_path: str):
    """
    Opens a Zarr store and caches the Dataset object.
    Subsequent calls with the same path will instantly return the cached object.
    """
    print(f"Opening and caching Zarr store: {zarr_path}")
    # consolidated=True speeds up opening if your Zarr store was saved with consolidated metadata
    return xr.open_zarr(zarr_path, consolidated=True)

def apply_colormap(data_array, vmin, vmax, cmap_name="viridis"):
    """Normalizes a 2D numpy array and applies a matplotlib colormap, returning RGBA."""
    # Handle NaN values (nodata)
    mask = np.isnan(data_array) | (data_array <= -9999) 
    
    # Handle Scientific Colormaps and Normalization
    if cmap_name == "vik":
        cmap = cmc.vik
        # TwoSlopeNorm requires the center (0) to be strictly between vmin and vmax
        if vmin < 0 < vmax:
            norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=0.0, vmax=vmax)
            # Using np.ma.masked_invalid to prevent warnings when normalizing NaNs
            norm_data = norm(np.ma.masked_invalid(data_array))
        else:
            # Fallback if user sets limits that don't cross zero
            norm_data = np.clip((data_array - vmin) / (vmax - vmin), 0, 1)
            
    elif cmap_name == "batlow":
        cmap = cmc.batlow
        norm_data = np.clip((data_array - vmin) / (vmax - vmin), 0, 1)
        
    else:
        cmap = cm.get_cmap(cmap_name)
        norm_data = np.clip((data_array - vmin) / (vmax - vmin), 0, 1)
    
    # Apply colormap
    rgba = cmap(norm_data)
    
    # Set nodata pixels to completely transparent
    rgba[mask, 3] = 0.0 
    
    # Convert from float [0-1] to uint8 [0-255]
    return (rgba * 255).astype(np.uint8)


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


def fetch_zarr_data(zarr_path, bbox, width, height, epoch_idx):
    """Extracts a 2D array from Zarr, interpolated exactly to width x height."""
    xmin, ymin, xmax, ymax = bbox
    
    # Open the Zarr store. 
    #ds = xr.open_zarr(zarr_path)
    ds = get_cached_zarr(zarr_path) # call the cached metadata for performance
    
    # Create target coordinates 
    target_x = np.linspace(xmin, xmax, width)
    target_y = np.linspace(ymax, ymin, height)
    
    # Slice desired epoch
    single_epoch_data = ds['speed'].isel(time=int(epoch_idx))
    
    # Interpolate directly to the required tile size.
    subset = single_epoch_data.interp(x=target_x, y=target_y, method="nearest")
    
    # Return the raw 2D numpy array for the requested epoch
    return subset.values


def render_array_to_png(data_array, vmin, vmax, cmap_name="viridis"):
    """Takes a raw 2D numpy array, applies colormaps, and converts it to a PNG."""
    rgba_img = apply_colormap(data_array, vmin, vmax, cmap_name)
    pil_img = Image.fromarray(rgba_img)
    
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return buf.getvalue()

