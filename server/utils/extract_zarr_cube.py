import xarray as xr
import geopandas as gpd
from shapely.geometry import shape
import pandas as pd
import numpy as np
import os
import rioxarray 
import uuid
import platform
from pathlib import Path
from datetime import datetime
import sys
import dask
import dask.array

# Import your existing paths
from utils.citations import generate_citation_text

# Set zarr store depending on operating system
current_os = platform.system()
is_wsl = "WSL_DISTRO_NAME" in os.environ
if current_os == "Windows" or is_wsl:
    root_drive = "/mnt/r" if is_wsl else "R:"
    DATA_STORES = {
        'Greenland': {
            'path': Path(f"{root_drive}/SCADI/output/Sentinel1/Greenland/mosaic/subregions/lev/date_pair_cubed.zarr"), 
            'crs': "EPSG:3413"
        },
        'Antarctica': {
            'path': Path(f"{root_drive}/SCADI/output/Sentinel1/Antarctica/mosaic/subregions/peninsula/date_pair_cubed.zarr"), 
            'crs': "EPSG:3031"
        }
    }
else:
    DATA_STORES = {
        'Greenland': {
            'path': Path("/mnt/grio1/Shared/SHIVER/data/Greenland/date_pair_cubed.zarr"), 
            'crs': "EPSG:3413"
        },
        'Antarctica': {
            'path': Path("/mnt/grio1/Shared/SHIVER/data/Antarctica/date_pair_cubed.zarr"), 
            'crs': "EPSG:3031"
        }
    }

# Set export directory
if current_os == "Windows" or is_wsl:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    export_dir = os.path.join(base_dir, "static", "exports")
    os.makedirs(export_dir, exist_ok=True)
else: 
    export_dir = Path("/mnt/grio1/Shared/SHIVER/data/exports")
    os.makedirs(export_dir, exist_ok=True)


# --- Extract the cube ---
def generate_netcdf_cube(
    geojson_geometry: dict,
    date_range: tuple[str, str], 
    variables: list[str] = ["s_filt", "u_filt", "v_filt", "s_raw", "u_raw", "v_raw"], 
    frequency: str = "native"
) -> tuple[str, str, str,  str]:
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
    ds = xr.open_zarr(store_info['path'], consolidated=True, chunks={})
    
    # 4. Crop spatial and time domain - note error values will therefore vary slightly depending on the time period selected
    print(f"Subsetting spatially and temporally...")
    buffer = 200 
    y_slice = slice(maxy + buffer, miny - buffer) if ds.y[0] > ds.y[-1] else slice(miny - buffer, maxy + buffer)
    
    subset = ds.sortby("time").sel(
        x=slice(minx - buffer, maxx + buffer), 
        y=y_slice,
        time=slice(date_range[0], date_range[1])
    )

    if subset.time.size == 0:
        raise ValueError("No data found inside the selected date range.")
        
    # 5. Calculate error 
    added_errors = {}
    for comp, rock, off in [('u', 'u_err_rock', 'u_err_off_ice'), ('v', 'v_err_rock', 'v_err_off_ice')]:
        if rock in subset and off in subset:
            err_da = subset[rock].fillna(subset[off]).fillna(0)
            fill_val = err_da.where(err_da != 0).mean()
            err_da = err_da.where(err_da != 0, fill_val)
            added_errors[f'{comp}_error'] = np.abs(err_da)

    if 'u_error' in added_errors and 'v_error' in added_errors:
        added_errors['s_error'] = np.sqrt(added_errors['u_error']**2 + added_errors['v_error']**2)
    
    # Add these new variables to the subset dataset
    for name, da in added_errors.items():
        subset[name] = da
    
    # 6. Select variables
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

    
    # 7. Clip to polygon boundaries
    print("Clipping data to exact polygon shape...")
    try:
        subset.rio.write_crs(target_crs, inplace=True)
        subset = subset.rio.clip(
            gdf_proj.geometry, 
            crs=target_crs, 
            drop=False, 
            invert=False,
            all_touched=True
        )
    except Exception as e:
        print(f"Clipping failed: {e}. Returning unclipped bounding box.")
    
    
    # 8. Temporal Resampling (Aggregation)
    ref_var = list(subset.data_vars)[0] # Pick a reference var to count valid pixels in
    if frequency != "native":
        print(f"Aggregating data...")
        # A. Define Resampler
        resampler = subset.resample(time=frequency)
        
        # B. Calculate Components
        ds_mean = resampler.mean(dim="time", keep_attrs=True)
        ds_std = resampler.std(dim="time", keep_attrs=True)
        
        # Count is the same for all variables from the same sensor, so we just pick one
        ref_var = list(subset.data_vars)[0]
        ds_count = subset[ref_var].resample(time=frequency).count(dim="time", keep_attrs=True)
        ds_count.name = "measurement_count"

        # C. Rename STD variables to prevent collision
        # e.g., 'u_filt' -> 'u_filt_std'
        rename_map = {var: f"{var}_std" for var in ds_std.data_vars}
        ds_std = ds_std.rename(rename_map)
        
        # D. Merge everything into one dataset
        subset = xr.merge([ds_mean, ds_std, ds_count])
    else:
        # Handle duplicate dates if using native resolution
        if not subset.indexes['time'].is_unique:
            print(f"Duplicate mid-dates detected in {region}. Applying negligible time offsets to preserve all pairs...")
            time_series = pd.Series(subset.time.values) # Extract time values to pandas to easily count duplicates
            dup_offsets = time_series.groupby(time_series).cumcount() # cumcount() returns 0 for the first occurrence, 1 for the second, etc.
            new_times = time_series + pd.to_timedelta(dup_offsets, unit='s') # Add 1 second per duplicate level to force uniqueness
            subset = subset.assign_coords(time=new_times.values) # Reassign the uniquely shifted times back to the dataset
            subset = subset.sortby('time') # Re-sort to ensure strict chronological order
            
            #print(f"Duplicate dates detected in {region}. Averaging...")
            # subset = subset.groupby("time").mean(dim="time", keep_attrs=True) # average the layers
            #subset = subset.drop_duplicates(dim="time", keep="first") # Or just keep first layer? Much faster but less robust.
            
    
    # 9. metadata
    print(f"Adding metadata to NetCDF.")
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
            
    # C. Calculate dates accounting for aggregation frequency
    print(f"Calculating epoch dates and mode time separation.")
    raw_first = pd.to_datetime(subset.time.values.min())
    raw_last = pd.to_datetime(subset.time.values.max())
    epochs = len(subset.time)
    
    if frequency != "native":
        freq_upper = str(frequency).upper()
        if "M" in freq_upper:  # Monthly
            first_date = raw_first.strftime('%Y-%m-01')
            last_date = (raw_last + pd.offsets.MonthEnd(0)).strftime('%Y-%m-%d')
        elif "Y" in freq_upper or "A" in freq_upper:  # Yearly
            first_date = raw_first.strftime('%Y-01-01')
            last_date = (raw_last + pd.offsets.YearEnd(0)).strftime('%Y-%m-%d')
        else:  # Weekly or custom rolling offsets
            first_date = raw_first.strftime('%Y-%m-%d')
            last_date = raw_last.strftime('%Y-%m-%d')
            
        # Dynamically calculate temporal resolution step size from the aggregated dimension
        if epochs > 1:
            time_diffs = np.diff(subset.time.values) / np.timedelta64(1, 'D')
            mode_vals = pd.Series(time_diffs).mode()
            mode_res = round(float(mode_vals.iloc[0]), 1) if not mode_vals.empty else round(float(time_diffs.mean()), 1)
        else:
            mode_res = "Variable"
    else:
        # Native mode tracks the raw satellite pass offset properties
        first_date = raw_first.strftime('%Y-%m-%d')
        last_date = raw_last.strftime('%Y-%m-%d')
        mode_res = "N/A"
        if "time_separation" in subset:
            sample_size = min(1000, subset["time_separation"].size)
            flat_vals = subset["time_separation"].data.flatten()[:sample_size]
            mode_vals = pd.Series(flat_vals).dropna().mode()
            if not mode_vals.empty:
                mode_res = round(float(mode_vals.iloc[0]), 2)
    
    # D. Generate citation text 
    print(f"Generating citation text.")
    # SHIVER Row
    shiver_citations = (
        "SHIVER tool: Davison, B. J. (2026). SHeffield Ice Velocity ExploreR (SHIVER): initial release (Version v1.0.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.21378057"
        "SHIVER zarr compilation method: Davison, B. J. (2026). SHeffield Ice Velocity ExploreR (SHIVER): A unified satellite-derived ice velocity dataset for Earth's ice sheets (Version v[specify version number]) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.21375859"
        "SHIVER method paper: Davison, B. J. et al. (in prep). The SHeffield Ice Velocity ExploreR (SHIVER): an online tool for low latency exploration, analysis and sub-setting of unified satellite-derived ice velocity data for Earth's ice sheets. [specify journal]. https://doi.org/10.xxxx/XXXXXXX"
    )
    
    # Get the SHIFT citation
    full_cite = generate_citation_text(["SHIFT"], region)
    delimiter = "cite these original sources:\n\n* "
    clean_cite = full_cite.split(delimiter)[1].strip() if delimiter in full_cite else full_cite.split("* ")[-1].strip()
    
    summary_rows = [
        {
            "Data Source": "SHIVER",
            "First Date": "",
            "Last Date": "",
            "Mode Temporal Resolution (days)": "",
            "Epochs (Measurements)": "",
            "Citation": shiver_citations
        },
        {
            "Data Source": "SHIFT",
            "First Date": first_date,
            "Last Date": last_date,
            "Mode Temporal Resolution (days)": mode_res,
            "Epochs (Measurements)": epochs,
            "Citation": clean_cite
        }
    ]
    
    csv_text = pd.DataFrame(summary_rows).to_csv(index=False)
                
    # E. Global Attributes (Point 1)
    print(f"Setting global NetCDF attributes.")
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
        'date_created': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'acknowledgment': full_cite
    }
        
    
    # 10. QGIS Compatibility
    print(f"Ensuring CRS compatibility.")
    # Ensure a CRS variable exists (rioxarray magic)
    if subset.rio.crs is None:
        subset.rio.write_crs(target_crs, inplace=True)
    
    # 11. Save
    print(f"Preparing encoding and saving...")
    # Prepare encoding for compression
    encoding = {}
    for var in subset.data_vars:
        # Handle string arrays (like data_source) safely without float _FillValues
        if subset[var].dtype.kind in 'UOS': 
            encoding[var] = {'zlib': True, 'complevel': 5}
        else:
            encoding[var] = {'zlib': True, 'complevel': 5, 'shuffle': True, '_FillValue': -9999.0}
            
        # Specific override for measurement_count to save space
        if var == "measurement_count":
             encoding[var]['dtype'] = 'int16'
             encoding[var]['_FillValue'] = -1
             
    # Force identical time encoding across ALL data cubes
    # This prevents the int64/scipy crash and guarantees consistency
    encoding['time'] = {
        'units': 'days since 1950-01-01',
        'calendar': 'proleptic_gregorian',
        'dtype': 'float64',
        '_FillValue': None
    }
        
    # Get the directory of this script, then go up to 'server/static/exports'
    #base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    #export_dir = os.path.join(base_dir, "static", "exports")
    #os.makedirs(export_dir, exist_ok=True)
    
    # Generate a short random ID (8 chars)
    unique_id = uuid.uuid4().hex[:8]
    
    # Define output filename
    filename = f"{region}_{frequency}_{date_range[0]}_{date_range[1]}_{unique_id}.nc"
    output_path = os.path.join(export_dir, filename)

    # Save to this specific path
    subset.to_netcdf(output_path, encoding=encoding, engine='netcdf4', format='NETCDF4')    
    print(f"Saved cube to: {output_path}")

    return output_path, region, full_cite, csv_text