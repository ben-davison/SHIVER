import xarray as xr
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import numpy as np
from pathlib import Path
import platform
import os
import warnings
from scipy.signal import savgol_filter
from functools import lru_cache

# --- 1. CONFIGURATION & ENVIRONMENT DETECTION ---
current_os = platform.system()
is_wsl = "WSL_DISTRO_NAME" in os.environ
if current_os == "Windows" or is_wsl:
    print("Environment: Windows (Multi-Source Data)")
    root_drive = "/mnt/r" if is_wsl else "R:"
    DATA_STORES = {
        'Greenland': {
            'path': Path(f"{root_drive}/SCADI/output/Sentinel1/Greenland/mosaic/subregions/lev/greenland_multisource_velocity_timeseries.zarr"), 
            'crs': "EPSG:3413"
        },
        'Antarctica': {
            'path': Path(f"{root_drive}/SCADI/output/Sentinel1/Antarctica/mosaic/subregions/peninsula/antarctica_multisource_velocity_timeseries.zarr"), 
            'crs': "EPSG:3031"
        }
    }
else:
    print("Environment: Linux (HPC Production - Multi-Source)")
    DATA_STORES = {
        'Greenland': {
            'path': Path("/mnt/grio1/Shared/SHIVER/data/Greenland/live/greenland_multisource_velocity_timeseries.zarr"), 
            'crs': "EPSG:3413"
        },
        'Antarctica': {
            'path': Path("/mnt/grio1/Shared/SHIVER/data/Antarctica/live/antarctica_multisource_velocity_timeseries.zarr"), 
            'crs': "EPSG:3031"
        }
    }
    
@lru_cache(maxsize=8)
def get_cached_timeseries_zarr(zarr_path):
    """
    Opens the time-series optimized Zarr store, sorts the time coordinate,
    and caches the resulting xarray Dataset in memory.
    """
    print(f"Opening and caching time-series Zarr store: {zarr_path}")
    # Cache the sorted dataset for performance
    return xr.open_zarr(zarr_path, consolidated=True).sortby('time')


def _empty_site_response(status="error", message=""):
    """
    Returns a standardized empty structure to guarantee downstream 
    routers/serializers never suffer from a KeyError.
    """
    return {
        "status": status,
        "message": message,
        "data": {
            "dates": [],
            "error": [],
            "dt": [],
            "data_source": [],
            "count": [],
            "speed": {
                "raw": [],
                "smoothed": []
            }
        }
    }

def get_multi_glacier_timeseries(
    location_input, 
    buffer=500, 
    sources=None, # List of strings to filter by
    name_column=None, 
    gap_fill=24,
    win_raw=25,
    win_daily=25,
    poly=2
):
    results = {}
    
    # 1. Parse Input
    gdf = _load_input_to_gdf(location_input)
    if gdf.empty:
        return {"error": "Input file contains no geometries."}
    
    # 1b. Limit extraction to ten locations
    if len(gdf) > 10:
        gdf = gdf.head(10)
        results["warning"] = "File contained more than 10 locations. Only the first 10 were extracted."

    # 2. Detect Region
    first_geom = gdf.geometry.iloc[0]
    ref_lat = first_geom.centroid.y
    region = 'Antarctica' if ref_lat < 0 else 'Greenland'
    store_info = DATA_STORES[region]
    
    # 3. Open Zarr
    try:
        #ds = xr.open_zarr(store_info['path'], consolidated=True).sortby('time')
        ds = get_cached_timeseries_zarr(store_info['path']) # read the cached zarr
    except Exception as e:
        return {"error": f"Could not open multi-source data store: {str(e)}"}

    # 4. Iterate Sites
    for idx, row in gdf.iterrows():
        site_name = f"Site_{idx}"
        if name_column and name_column in gdf.columns: site_name = str(row[name_column])
        elif 'name' in gdf.columns: site_name = str(row['name'])
        elif 'Name' in gdf.columns: site_name = str(row['Name'])

        current_buffer = buffer
        if 'buffer' in gdf.columns:
            try: current_buffer = float(row['buffer'])
            except (ValueError, TypeError): current_buffer = buffer
            
        site_data = _process_single_site_multi(
            ds, row.geometry, store_info['crs'], current_buffer, sources,
            gap_fill, win_raw, win_daily, poly
        )
        
        centroid = row.geometry.centroid
        meta = {
            "site_name": site_name,
            "region": region,
            "buffer_used": current_buffer,
            "lat": round(centroid.y, 5),
            "lon": round(centroid.x, 5),
            "type": "Polygon" if isinstance(row.geometry, Polygon) else "Point",
            "sources_requested": sources if sources else "All",
            "params": { "gap": gap_fill, "win_raw": win_raw, "win_daily": win_daily, "poly": poly }
        }

        if 'meta' in site_data:
            site_data['meta'].update(meta)
        else:
            site_data['meta'] = meta
            
        results[site_name] = site_data

    return results

def _process_single_site_multi(ds, geometry, target_crs, buffer, sources, gap_fill, win_raw, win_daily, poly):
    temp_gdf = gpd.GeoDataFrame({'geometry': [geometry]}, crs="EPSG:4326").to_crs(target_crs)
    proj_geom = temp_gdf.geometry.iloc[0]
    
    x_min, x_max = ds.x.min().item(), ds.x.max().item()
    y_min, y_max = ds.y.min().item(), ds.y.max().item()
    if y_min > y_max: y_min, y_max = y_max, y_min

    px, py = proj_geom.centroid.x, proj_geom.centroid.y
    if not (x_min <= px <= x_max) or not (y_min <= py <= y_max):
        return _empty_site_response("error", "Location outside data coverage.")
    
    is_single_pixel = False
    if isinstance(proj_geom, Point):
        if buffer <= 0: is_single_pixel = True 
        else: minx, miny, maxx, maxy = proj_geom.buffer(buffer).bounds
    else:
        if buffer > 0: proj_geom = proj_geom.buffer(buffer)
        minx, miny, maxx, maxy = proj_geom.bounds

    if not is_single_pixel:
        y_slice = slice(maxy, miny) if ds.y[0] > ds.y[-1] else slice(miny, maxy)
        try:
            subset = ds.sel(x=slice(minx, maxx), y=y_slice)
            if subset.x.size == 0 or subset.y.size == 0: is_single_pixel = True 
        except Exception: is_single_pixel = True

    # Deal with time bounds
    if is_single_pixel:
        try:
            subset = ds.sel(x=proj_geom.centroid.x, y=proj_geom.centroid.y, method='nearest')
        except Exception as e:
            return _empty_site_response("error", f"Pixel selection failed: {e}")
            
    if 'time_bnds' in subset.data_vars or 'time_bnds' in subset.coords:
        tb = subset['time_bnds']
        if len(tb.dims) >= 2:
            bnd_dim = [d for d in tb.dims if d != 'time'][0]
            # Extract start and end arrays
            t0 = tb.isel({bnd_dim: 0})
            t1 = tb.isel({bnd_dim: 1})
            # Calculate difference in days safely using numpy timedelta division
            dt_days = (t1 - t0) / np.timedelta64(1, 'D')
            subset = subset.assign(time_separation=dt_days)
        else:
            subset = subset.assign(time_separation=xr.full_like(subset['time'], 12.0, dtype=float))
        
        # Drop time_bnds so it doesn't break pandas to_dataframe()
        subset = subset.drop_vars('time_bnds')
    else:
        subset = subset.assign(time_separation=xr.full_like(subset['time'], 12.0, dtype=float))


    # 1. Extraction and Spatial Aggregation 
    if is_single_pixel:
        df = subset[['speed', 'speed_error', 'data_source', 'time_separation']].to_dataframe()
        df['valid_count'] = subset['speed'].notnull().astype(int).to_series()
    else:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            spatial_median = subset[['speed', 'speed_error']].median(dim=['x', 'y'])
        
        valid_count = subset['speed'].notnull().sum(dim=['x', 'y'])
        
        # Combine into a lightweight time-indexed pandas dataframe
        df = spatial_median.to_dataframe()
        if 'x' in subset['data_source'].dims:
            df['data_source'] = subset['data_source'].isel(x=0, y=0).values
        else:
            df['data_source'] = subset['data_source'].values
            
        if 'x' in subset['time_separation'].dims:
            df['time_separation'] = subset['time_separation'].isel(x=0, y=0).values
        else:
            df['time_separation'] = subset['time_separation'].values
            
        df['valid_count'] = valid_count.values

    # 2. Filter by Data Source
    if sources is not None and len(sources) > 0:
        df = df[df['data_source'].astype(str).isin(sources)]
        
    if df.empty or df['speed'].dropna().empty:
        return _empty_site_response("error", "No valid data or all selected sources masked/NaN")
    
    # Check time separation
    #df['time_separation'] = df['time_separation'] - 1.0
    df['time_separation'] = df['time_separation'].apply(lambda x: x if x > 0 else 0.5).fillna(12.0)
    df = df.sort_index()
    
    if df.index.duplicated().any():
        df = df.groupby(level=0).first()

    # =========================================================================
    # PROCESSING LOOP
    # =========================================================================
    
    # --- OUTLIER REJECTION ---
    # Apply physical speed limits
    df.loc[(df['speed'] < -100) | (df['speed'] > 100000), 'speed'] = np.nan
    
    # Apply a rolling Z-score filter to drop extreme outliers before any math
    rolling_mean = df['speed'].rolling(window=5, center=True, min_periods=1).mean()
    rolling_std = df['speed'].rolling(window=5, center=True, min_periods=1).std()
    
    # Use overall std as fallback if rolling std is 0 or NaN (e.g., too few points)
    fallback_std = df['speed'].std()
    if pd.isna(fallback_std) or fallback_std == 0: fallback_std = 1.0
    rolling_std = rolling_std.fillna(fallback_std).replace(0, fallback_std)
    
    # Flag points that deviate more than 3 standard deviations from local mean
    outliers = (df['speed'] - rolling_mean).abs() > (3 * rolling_std)
    df.loc[outliers, 'speed'] = np.nan

    # Create combined time vector (exact times and regular times)
    exact_idx = df.index
    daily_idx = pd.date_range(start=exact_idx.min().floor('D'), end=exact_idx.max().ceil('D'), freq='D')
    full_idx = exact_idx.union(daily_idx).sort_values()

    # Map the raw data onto this combined timeline
    df_daily = df.reindex(full_idx) 
    valid_dates_mask = df_daily['speed'].notnull() # only keep points where speed is not null
    
    def clean_nans(data_series):
        if hasattr(data_series, 'values'): data_series = data_series.values 
        if len(data_series) == 0: return []
        return [x if (pd.notnull(x) and (isinstance(x, str) or np.isfinite(x))) else None for x in data_series]

    output_data = {
        # Export as ISO strings so the frontend gets the exact time (e.g., 1986-07-02T06:06:19)
        "dates": full_idx.strftime('%Y-%m-%dT%H:%M:%S').tolist(), 
        "error": clean_nans(np.round(df_daily['speed_error'].astype(float), 2)),
        "dt": clean_nans(np.round(df_daily['time_separation'].astype(float), 1)),
        "data_source": clean_nans(df_daily['data_source']), 
        "count": df_daily['valid_count'].fillna(0).astype(int).tolist()
    }

    current_speed_series = df['speed']
    
    # --- STEP 1: RAW SMOOTHING (Points) ---
    daily_temp = current_speed_series.reindex(full_idx)
    daily_filled = daily_temp.interpolate(method='time', limit=gap_fill)
    processed_raw_series = df_daily['speed'] 
    
    try:
        temp_series = daily_filled.interpolate(method='time', limit_direction='both')
        curr_len = len(temp_series)
        effective_window = win_raw
        if curr_len < effective_window: effective_window = curr_len
        if effective_window % 2 == 0: effective_window -= 1 

        if effective_window >= 3:
            smoothed_values = savgol_filter(temp_series.values, window_length=effective_window, polyorder=poly)
            daily_smoothed_raw = pd.Series(smoothed_values, index=full_idx)
            processed_raw_series = daily_smoothed_raw.where(valid_dates_mask)
    except Exception:
        pass

    # --- STEP 2: WEIGHTED DAILY AVERAGE ---
    capped_separation = df['time_separation'].clip(upper=gap_fill)
    time_sep_days = pd.to_timedelta(capped_separation, unit='D')
    starts_arr = (df.index - (time_sep_days / 2)).dt.floor('D').values
    ends_arr   = (df.index + (time_sep_days / 2)).dt.ceil('D').values
    daily_stack = []
    
    # Pre-extract numpy arrays to bypass slow Pandas row indexers inside the loop
    speeds_arr = current_speed_series.values
    dt_arr = df['time_separation'].values
    times_arr = df.index
    
    for i in range(len(df)):
        if pd.isna(speeds_arr[i]): continue 
        
        val_to_use = speeds_arr[i]
        try:
            if pd.notnull(processed_raw_series.loc[times_arr[i]]):
                val_to_use = processed_raw_series.loc[times_arr[i]]
        except: pass
        
        dt_val = dt_arr[i] if (pd.notnull(dt_arr[i]) and dt_arr[i] >= 1) else 1.0
        weight_val = 1.0 / dt_val

        # Lightening the creation loop
        date_rng = pd.date_range(start=starts_arr[i], end=ends_arr[i], freq='D')
        if not date_rng.empty:
            daily_stack.append(pd.DataFrame({
                'date': date_rng, 
                'speed': val_to_use,
                'weight': weight_val
            }))

    if daily_stack:
        big_df = pd.concat(daily_stack, ignore_index=True)
        big_df['weighted_speed'] = big_df['speed'] * big_df['weight']
        grouped = big_df.groupby('date')
        daily_ts = grouped['weighted_speed'].sum() / grouped['weight'].sum()
        daily_ts = daily_ts.reindex(full_idx)
    else:
        daily_ts = pd.Series(dtype=float, index=full_idx)

    # --- DAILY SMOOTHING & GAP RE-MASKING ---
    daily_ts_filled = daily_ts.interpolate(method='time', limit=gap_fill)
    daily_final = daily_ts.copy() 
    
    try:
        temp_series_daily = daily_ts_filled.interpolate(method='time', limit_direction='both')
        curr_len_d = len(temp_series_daily)
        eff_win_daily = win_daily
        if curr_len_d < eff_win_daily: eff_win_daily = curr_len_d
        if eff_win_daily % 2 == 0: eff_win_daily -= 1

        if eff_win_daily >= 3:
            smooth_vals_daily = savgol_filter(temp_series_daily.values, window_length=eff_win_daily, polyorder=poly)
            daily_final = pd.Series(smooth_vals_daily, index=full_idx)
            daily_final[daily_ts_filled.isna()] = np.nan
    except Exception: 
        pass
        
    trend_on_dates = daily_final 

    output_data['speed'] = {
        "raw": clean_nans(np.round(processed_raw_series.astype(float), 2)), 
        "smoothed": clean_nans(np.round(trend_on_dates.astype(float), 2))              
    }

    return {
        "status": "success",
        "message": "Data processed successfully.",
        "data": output_data
    }

def _load_input_to_gdf(loc_input):
    # Same helper function as original file...
    if isinstance(loc_input, (str, Path)):
        path_str = str(loc_input)
        if path_str.lower().endswith('.zip'):
            return gpd.read_file(f"zip://{path_str}")
        return gpd.read_file(path_str)
    
    if isinstance(loc_input, list):
        if len(loc_input) > 0 and isinstance(loc_input[0], (int, float)):
             loc_input = [loc_input]
        geoms = [Point(lon, lat) for lat, lon in loc_input]
        return gpd.GeoDataFrame(geometry=geoms, crs="EPSG:4326")
    
    if isinstance(loc_input, gpd.GeoDataFrame):
        return loc_input.to_crs("EPSG:4326")

    raise ValueError("Unsupported input format.")