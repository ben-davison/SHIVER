import xarray as xr
import geopandas as gpd
from shapely.geometry import shape
import pandas as pd
import numpy as np
import os
import rioxarray 
import uuid
from datetime import datetime

# Import your existing paths
from utils.extract_zarr_ts import DATA_STORES 

# --- estimate cube size ---
def estimate_cube_size(geojson_geometry, date_range, variables, frequency):
    """
    Opens the Zarr (lazy), subsets metadata, and returns estimated size in MB.
    Does NOT load actual data.
    """
    # 1. Parse Geometry & Detect Region
    user_shape = shape(geojson_geometry)
    
    if user_shape.centroid.y < 0:
        region = "Antarctica"
        target_crs = "EPSG:3031"
    else:
        region = "Greenland"
        target_crs = "EPSG:3413"
        
    store_info = DATA_STORES.get(region)
    if not store_info:
        raise ValueError(f"Region not found for lat: {user_shape.centroid.y}")


    # 2. Project Geometry to Data CRS
    gdf = gpd.GeoDataFrame({'geometry': [user_shape]}, crs="EPSG:4326")
    gdf_proj = gdf.to_crs(target_crs)
    minx, miny, maxx, maxy = gdf_proj.total_bounds
    
    # 3. Open Zarr Store (Lazy Load)
    ds = xr.open_zarr(store_info['path'], consolidated=True, chunks=None)
    
    # 4. Variable Selection
    available_vars = [v for v in variables if v in ds]
    ds = ds[available_vars]

    # 5. Spatial Subsetting (Bounding Box)
    # We do this FIRST to reduce the data we have to sort/process
    buffer = 200 
    y_slice = slice(maxy + buffer, miny - buffer) if ds.y[0] > ds.y[-1] else slice(miny - buffer, maxy + buffer)
    subset = ds.sel(
        x=slice(minx - buffer, maxx + buffer), 
        y=y_slice
    )
    
    # 6. Sort and crop time
    subset = subset.sortby("time")
    subset = subset.sel(time=slice(date_range[0], date_range[1]))
    
    
    # 7. Estimate data volume 
    raw_nbytes = subset.nbytes 
    if raw_nbytes == 0:
        return 0

    # Adjust depending on frequency of output
    if frequency == "native":
        return raw_nbytes / (1024 * 1024)

    native_steps = subset.time.size
    if native_steps == 0: return 0

    # Calculate how many steps the target frequency produces
    try:
        # Generate the theoretical date range
        # Note: 'frequency' must be a valid pandas offset alias (MS, QS, AS, etc.)
        # We use the start/end from the user request
        target_range = pd.date_range(start=date_range[0], end=date_range[1], freq=frequency)
        target_steps = len(target_range)
    except Exception:
        # Fallback if frequency string is weird: assume no reduction
        target_steps = native_steps

    if target_steps == 0: target_steps = 1
    
    # Ratio: e.g., if Native has 100 steps and Annual has 2, ratio is 0.02
    ratio = target_steps / native_steps
    
    # Apply ratio to size
    estimated_mb = (raw_nbytes * ratio) / (1024 * 1024)
    
    # If resampling, reduce size roughly by ratio of time steps
    # (This is optional, nbytes on the raw subset is a safe "Upper Bound")
    return estimated_mb




# --- Extract the cube ---
def generate_netcdf_cube(
    geojson_geometry: dict,
    date_range: tuple[str, str], 
    variables: list[str] = ["s_filt", "u_filt", "v_filt", "s_raw", "u_raw", "v_raw"], # Adjusted to match your defaults
    frequency: str = "native",
    max_size_mb: int = 500
) -> str:
    """
    Generates a QGIS-ready NetCDF file for a specific ROI and time period.
    Handles unsorted dates and duplicates automatically.
    """
    
    # 1. Parse Geometry & Detect Region
    user_shape = shape(geojson_geometry)
    
    if user_shape.centroid.y < 0:
        region = "Antarctica"
        target_crs = "EPSG:3031"
    else:
        region = "Greenland"
        target_crs = "EPSG:3413"
        
    store_info = DATA_STORES.get(region)
    if not store_info:
        raise ValueError(f"Region not found for lat: {user_shape.centroid.y}")


    # 2. Project Geometry to Data CRS
    gdf = gpd.GeoDataFrame({'geometry': [user_shape]}, crs="EPSG:4326")
    gdf_proj = gdf.to_crs(target_crs)
    minx, miny, maxx, maxy = gdf_proj.total_bounds
    
    
    # 3. Open Zarr Store (Lazy Load)
    ds = xr.open_zarr(store_info['path'], consolidated=True, chunks=None)
    
    # 4. Calculate error (Before filtering/resampling)
    def calc_error_component(rock_var, office_var):
        if rock_var not in ds or office_var not in ds:
            return None
        
        err = ds[rock_var].fillna(ds[office_var]).fillna(0)
        
        return err
    
    # 5. Spatial Subsetting (Bounding Box)
    print(f"Subsetting spatially...")
    buffer = 200 
    # Handle Y-axis orientation
    y_slice = slice(maxy + buffer, miny - buffer) if ds.y[0] > ds.y[-1] else slice(miny - buffer, maxy + buffer)
    subset = ds.sel( x=slice(minx - buffer, maxx + buffer), y=y_slice )
    
    # 6. Generate error fields
    # A. Calculate Component Errors (U and V)
    u_rock, u_off = 'u_err_rock', 'u_err_off_ice'
    v_rock, v_off = 'v_err_rock', 'v_err_off_ice'
    added_errors = {}
    for comp, rock, off in [('u', u_rock, u_off), ('v', v_rock, v_off)]:
        if rock in subset and off in subset:
            err_da = subset[rock].fillna(subset[off]).fillna(0)
            median_val = err_da.where(err_da != 0).median().values
            err_da = err_da.where(err_da != 0, median_val)
            added_errors[f'{comp}_error'] = np.abs(err_da)

    # B. Calculate Speed Error (Magnitude of U and V errors)
    if 'u_error' in added_errors and 'v_error' in added_errors:
        added_errors['s_error'] = np.sqrt(added_errors['u_error']**2 + added_errors['v_error']**2)

    # Add these new variables to the subset dataset
    for name, da in added_errors.items():
        subset[name] = da
    
    # 7. Select variables
    final_vars = list(variables) 
    # 7b. Add V error if any V variable is requested
    if any('v' in v.lower() for v in variables) and 'v_error' in subset:
        final_vars.append('v_error')
    # 7c. Add U error if any U variable is requested
    if any('u' in v.lower() for v in variables) and 'u_error' in subset:
        final_vars.append('u_error')
    # 7d. Add S (Speed) error if any Speed variable is requested
    if any('s' in v.lower() for v in variables) and 's_error' in subset:
        final_vars.append('s_error')
    # 7a. Native Frequency check
    if frequency == "native":
        if 'time_separation' in ds:
            final_vars.append('time_separation')

    # Filter the dataset
    vars_to_keep = [v for v in final_vars if v in subset]
    subset = subset[vars_to_keep]

    
    # 8. Clip to polygon boundaries
    print("Clipping data to exact polygon shape...")
    try:
        # We must write the CRS to the xarray object so rioxarray knows how to interpret it
        subset.rio.write_crs(target_crs, inplace=True)
        
        # Clip
        # all_touched=True ensures we don't return empty data if the polygon is very thin
        # drop=False keeps the rectangular grid coordinates (required for NetCDF) but fills outside with NaN
        subset = subset.rio.clip(
            gdf_proj.geometry, 
            crs=target_crs, 
            drop=False, 
            invert=False,
            all_touched=True
        )
    except Exception as e:
        print(f"⚠️ Clipping failed: {e}. Returning unclipped bounding box.")
    # -----------------------------------

    
    # 9. Sort and crop time
    print(f"Sorting and cropping to time period...")
    subset = subset.sortby("time")
    subset = subset.sel(time=slice(date_range[0], date_range[1]))
    
    
    # 10. Temporal Resampling (Aggregation)
    ref_var = list(subset.data_vars)[0] # Pick a reference var to count valid pixels in
    if frequency != "native":
        print(f"Aggregating data...")
        # 1. Define Resampler
        resampler = subset.resample(time=frequency)
        
        # 2. Calculate Components
        ds_mean = resampler.mean(dim="time", keep_attrs=True)
        ds_std = resampler.std(dim="time", keep_attrs=True)
        
        # Count is the same for all variables from the same sensor, so we just pick one
        ref_var = list(subset.data_vars)[0]
        ds_count = subset[ref_var].resample(time=frequency).count(dim="time", keep_attrs=True)
        ds_count.name = "measurement_count"

        # 3. Rename STD variables to prevent collision
        # e.g., 'u_filt' -> 'u_filt_std'
        rename_map = {var: f"{var}_std" for var in ds_std.data_vars}
        ds_std = ds_std.rename(rename_map)
        
        # 4. Merge everything into one dataset
        subset = xr.merge([ds_mean, ds_std, ds_count])
    else:
        # Handle duplicate dates if using native resolution
        if not subset.indexes['time'].is_unique:
            print(f"Duplicate dates detected in {region}. Averaging...")
            # groupby('time').mean() automatically sorts and removes duplicates
            subset = subset.groupby("time").mean(dim="time", keep_attrs=True)
            
    
    # 11. metadata
    # A. Ensure CRS
    if subset.rio.crs is None:
        subset.rio.write_crs(target_crs, inplace=True)

    # B. Variable Attributes    
    for var_name in subset.variables:
        # Generic defaults
        subset[var_name].attrs['grid_mapping'] = 'spatial_ref'
        subset[var_name].attrs['coverage_content_type'] = 'physicalMeasurement'
        
        # Specifics based on name patterns
        lower_name = var_name.lower()
        
        # --- COORDINATES ---
        if var_name == 'x':
            subset[var_name].attrs['long_name'] = f"polar stereographic easting ({target_crs})"
            subset[var_name].attrs['units'] = "m"
            subset[var_name].attrs['standard_name'] = "projection_x_coordinate"
        elif var_name == 'y':
            subset[var_name].attrs['long_name'] = f"polar stereographic northing ({target_crs})"
            subset[var_name].attrs['units'] = "m"
            subset[var_name].attrs['standard_name'] = "projection_y_coordinate"
        elif var_name == 'time':
            subset[var_name].attrs['long_name'] = "time"
            subset[var_name].attrs['standard_name'] = "time"
            
        # --- NATIVE METADATA ---
        elif var_name == 'time_separation':
            subset[var_name].attrs['long_name'] = "time separation between image pairs in each measurement epoch"
            subset[var_name].attrs['units'] = "days"
            
        # --- STANDARD DEVIATION ---
        elif var_name.endswith("_std"):
            # Determine description based on the name string itself, not the base object
            # This solves the "order of operations" race condition.
            if 's_' in lower_name or var_name.startswith('s_'):
                base_desc = "ice surface velocity magnitude"
            elif 'u_' in lower_name or var_name.startswith('u_'):
                base_desc = "ice surface easting velocity"
            elif 'v_' in lower_name or var_name.startswith('v_'):
                base_desc = "ice surface northing velocity"
            else:
                base_desc = var_name.replace("_std", "") # Fallback

            subset[var_name].attrs['long_name'] = f"standard deviation of {base_desc}"
            subset[var_name].attrs['units'] = "m yr-1"
            subset[var_name].attrs['coverage_content_type'] = "auxiliaryInformation"
            subset[var_name].attrs.pop('standard_name', None)
            
        # --- MEASUREMENT COUNT ---
        elif var_name == "measurement_count":
             subset[var_name].attrs['long_name'] = "count of valid measurements used in aggregation"
             subset[var_name].attrs['units'] = "count"
             subset[var_name].attrs['coverage_content_type'] = "auxiliaryInformation"
             subset[var_name].attrs.pop('standard_name', None)
             
        # --- ERROR VARIABLES ---
        elif 'error' in lower_name:
            subset[var_name].attrs['units'] = "m yr-1"
            if 's_' in lower_name:
                subset[var_name].attrs['long_name'] = "magnitude of ice velocity error"
            elif 'u_' in lower_name:
                subset[var_name].attrs['long_name'] = "easting velocity error"
            elif 'v_' in lower_name:
                subset[var_name].attrs['long_name'] = "northing velocity error"
            
        # --- DATA VARIABLES ---
        elif 's_' in lower_name or var_name == 's':
            subset[var_name].attrs['long_name'] = "ice surface velocity magnitude"
            subset[var_name].attrs['units'] = "m yr-1"
        elif 'u_' in lower_name or var_name == 'u':
            subset[var_name].attrs['long_name'] = "ice surface easting velocity"
            subset[var_name].attrs['units'] = "m yr-1"
        elif 'v_' in lower_name or var_name == 'v':
            subset[var_name].attrs['long_name'] = "ice surface northing velocity"
            subset[var_name].attrs['units'] = "m yr-1"
               
                
    # C. Global Attributes (Point 1)
    time_start = pd.to_datetime(subset.time.values.min()).strftime('%Y%m%d')
    time_end = pd.to_datetime(subset.time.values.max()).strftime('%Y%m%d')
    
    subset.attrs = {
        'title': f"{region} Ice Velocity Cube",
        'author': 'Benjamin Davison and Andrew Sole',
        'creator_name': 'Benjamin Davison',
        'creator_email': 'b.j.davison@sheffield.ac.uk',
        'institution': 'University of Sheffield',
        'product_version': '1.0',
        'time_coverage_start': time_start,
        'time_coverage_end': time_end,
        'keywords': f"{region}, velocity, Sentinel-1",
        'Conventions': 'CF-1.8, ACDD-1.3',
        'date_created': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    estimated_mb = subset.nbytes / (1024 * 1024) # MB
    
    if estimated_mb > max_size_mb:
        raise ValueError(
            f"Resulting data cube is too large ({estimated_mb:.0f} MB). "
            f"Please reduce area or time range."
        )
    
    # 8. QGIS Compatibility
    # Ensure a CRS variable exists (rioxarray magic)
    if subset.rio.crs is None:
        subset.rio.write_crs(target_crs, inplace=True)
    
    # 9. Save
    # Prepare encoding for compression
    encoding = {}
    for var in subset.data_vars:
        encoding[var] = {'zlib': True, 'complevel': 5, 'shuffle': True, '_FillValue': -9999.0}
        if var == "measurement_count":
             encoding[var]['dtype'] = 'int16' # Force integer type to save space
             encoding[var]['_FillValue'] = -1
        
    # Get the directory of this script, then go up to 'server/static/exports'
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    export_dir = os.path.join(base_dir, "static", "exports")
    
    # Create the folder if it doesn't exist
    os.makedirs(export_dir, exist_ok=True)
    
    # Generate a short random ID (8 chars)
    unique_id = uuid.uuid4().hex[:8]
    
    # Define output filename
    filename = f"{region}_{frequency}_{date_range[0]}_{date_range[1]}_{unique_id}.nc"
    output_path = os.path.join(export_dir, filename)

    # Save to this specific path
    subset.to_netcdf(output_path)
    
    print(f"✅ Saved cube to: {output_path}")

    return output_path, region