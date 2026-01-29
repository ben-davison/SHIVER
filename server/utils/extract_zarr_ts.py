import xarray as xr
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import numpy as np
from pathlib import Path
import platform
from scipy.signal import savgol_filter

# --- 1. CONFIGURATION & ENVIRONMENT DETECTION ---

current_os = platform.system()

if current_os == "Windows":
    desktop_gr_path = Path("R:/SCADI/output/Sentinel1/Greenland/mosaic/subregions/lev/date_pair.zarr")
    desktop_ant_path = Path("R:/SCADI/output/Sentinel1/Antarctica/mosaic/subregions/peninsula/date_pair.zarr")

    if desktop_gr_path.exists():
        print("🖥️  Environment: Windows (Desktop - Full Data)")
        DATA_STORES = {
            'Greenland': {'path': desktop_gr_path, 'crs': "EPSG:3413"},
            'Antarctica': {'path': desktop_ant_path, 'crs': "EPSG:3031"}
        }
    else:
        print("💻  Environment: Windows (Laptop - Mini Data)")
        DATA_STORES = {
            'Greenland': {
                'path': Path("D:/work/Fellowship_Leeds/SCADI/output/Sentinel1/Greenland/mosaic/subregions/lev/mini_date_pair.zarr"),
                'crs': "EPSG:3413"
            },
            'Antarctica': {
                'path': Path("D:/work/Fellowship_Leeds/SCADI/output/Sentinel1/Antarctica/mosaic/subregions/peninsula/mini_date_pair.zarr"), 
                'crs': "EPSG:3031"
            }
        }
else:
    print("🚀 Environment: Linux (HPC Production)")
    base_hpc_path = Path("/mnt/parscratch/users/gg1bjd/SCADI/output/Sentinel1")
    DATA_STORES = {
        'Greenland': {
            'path': base_hpc_path / "Greenland/mosaic/subregions/lev/date_pair.zarr",
            'crs': "EPSG:3413"
        },
        'Antarctica': {
            'path': base_hpc_path / "Antarctica/mosaic/subregions/peninsula/date_pair.zarr",
            'crs': "EPSG:3031"
        }
    }

def get_glacier_timeseries(
    location_input, 
    buffer=500, 
    name_column=None, 
    variables=['s'], 
    quality=['filt'],
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

    # 2. Detect Region
    first_geom = gdf.geometry.iloc[0]
    ref_lat = first_geom.centroid.y
    region = 'Antarctica' if ref_lat < 0 else 'Greenland'
    store_info = DATA_STORES[region]
    
    # 3. Open Zarr
    try:
        ds = xr.open_zarr(store_info['path'], consolidated=True).sortby('time')
    except Exception as e:
        return {"error": f"Could not open data store: {str(e)}"}

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
            
        site_data = _process_single_site(
            ds, row.geometry, store_info['crs'], current_buffer, variables, quality,
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
            "variables": variables,
            "quality": quality,
            "params": { "gap": gap_fill, "win_raw": win_raw, "win_daily": win_daily, "poly": poly }
        }

        if 'meta' in site_data:
            site_data['meta'].update(meta)
        else:
            site_data['meta'] = meta
            
        results[site_name] = site_data

    return results


def _process_single_site(ds, geometry, target_crs, buffer, variables, quality_list, gap_fill, win_raw, win_daily, poly):

    temp_gdf = gpd.GeoDataFrame({'geometry': [geometry]}, crs="EPSG:4326").to_crs(target_crs)
    proj_geom = temp_gdf.geometry.iloc[0]
    
    x_min, x_max = ds.x.min().item(), ds.x.max().item()
    y_min, y_max = ds.y.min().item(), ds.y.max().item()
    if y_min > y_max: y_min, y_max = y_max, y_min

    px, py = proj_geom.centroid.x, proj_geom.centroid.y
    if not (x_min <= px <= x_max) or not (y_min <= py <= y_max):
        return {"status": "error", "message": "Location outside data coverage."}
    
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

    target_keys = []
    for v in variables:
        for q in quality_list:
            target_keys.append(f"{v}_{q}")
            
    base_vars = ['u_err_rock', 'u_err_off_ice', 'v_err_rock', 'v_err_off_ice', 'time_separation']
    vars_to_keep = list(set(target_keys + base_vars))
    
    if is_single_pixel:
        try:
            subset = ds.sel(x=proj_geom.centroid.x, y=proj_geom.centroid.y, method='nearest')
        except Exception as e:
            return {"status": "error", "message": f"Pixel selection failed: {e}"}
        
        count_col = target_keys[0] if target_keys else 's_filt'
        if count_col not in subset: count_col = 'time_separation'
        
        pixel_counts = subset[count_col].notnull().astype(int)
        df = subset[vars_to_keep].to_dataframe()
        df['valid_count'] = pixel_counts.to_series()
    else:
        count_col = target_keys[0] if target_keys else 's_filt'
        if count_col not in subset: count_col = 'time_separation'
        pixel_counts = subset[count_col].count(dim=['x', 'y'])
        df = subset[vars_to_keep].median(dim=['x', 'y'], keep_attrs=True).to_dataframe()
        df['valid_count'] = pixel_counts.to_series()

    present_keys = [k for k in target_keys if k in df.columns]
    if present_keys:
        df = df.dropna(subset=present_keys, how='all')
    
    if df.empty:
        return {"status": "error", "message": "All pixels masked/NaN"}

    u_err = df['u_err_rock'].fillna(df['u_err_off_ice']).fillna(0)
    v_err = df['v_err_rock'].fillna(df['v_err_off_ice']).fillna(0)
    u_err = u_err.replace(0, u_err.median())
    v_err = v_err.replace(0, v_err.median())
    
    df['error_m_yr'] = np.sqrt(u_err**2 + v_err**2)
    df = df.sort_index()
    
    if df.index.duplicated().any():
        agg_rules = {col: 'median' for col in df.columns if col != 'valid_count'}
        if 'valid_count' in df.columns: agg_rules['valid_count'] = 'sum'
        df = df.groupby(level=0).agg(agg_rules)

    # =========================================================================
    # PROCESSING LOOP
    # =========================================================================
    
    # 1. Create the Full Daily Index (The X-Axis)
    full_idx = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
    
    # 2. Identify which dates are "real" observation dates
    # We use this to mask the raw data later
    valid_dates_mask = pd.Series(False, index=full_idx)
    valid_dates_mask.loc[df.index] = True

    # Prepare common data arrays on the full timeline
    df_daily = df.reindex(full_idx) 

    def clean_nans(data_series):
        if hasattr(data_series, 'values'): data_series = data_series.values 
        if len(data_series) == 0: return []
        return [x if (pd.notnull(x) and np.isfinite(x)) else None for x in np.round(data_series, 1).tolist()]

    output_data = {
        "dates": full_idx.strftime('%Y-%m-%d').tolist(), 
        "error": clean_nans(df_daily['error_m_yr']),
        "dt": clean_nans(df_daily['time_separation']),
        "count": df_daily['valid_count'].fillna(0).astype(int).tolist()
    }

    for key in present_keys:
        current_speed_series = df[key]
        
        # --- STEP 1: RAW SMOOTHING (Points) ---
        # Strategy: Interpolate -> Smooth -> MASK back to original dates
        
        daily_temp = current_speed_series.reindex(full_idx)
        daily_filled = daily_temp.interpolate(method='time', limit=gap_fill)
        
        # Default: If smoothing fails, just use original raw values on the full timeline
        processed_raw_series = df_daily[key] 
        
        try:
            temp_series = daily_filled.interpolate(method='time', limit_direction='both')
            
            curr_len = len(temp_series)
            effective_window = win_raw
            if curr_len < effective_window:
                effective_window = curr_len
            if effective_window % 2 == 0: effective_window -= 1 

            if effective_window >= 3:
                smoothed_values = savgol_filter(temp_series.values, window_length=effective_window, polyorder=poly)
                daily_smoothed_raw = pd.Series(smoothed_values, index=full_idx)
                
                # We want the "raw" trace to contain the Smoothed Point values, 
                # but only on the days where original data existed.
                # All other days must be NaN so the chart doesn't draw points there.
                processed_raw_series = daily_smoothed_raw.where(valid_dates_mask)
                
        except Exception:
            pass

        # --- STEP 2: DAILY MEDIAN (Trend Line Calculation) ---
        time_sep_days = pd.to_timedelta(df['time_separation'], unit='D')
        starts = df.index - (time_sep_days / 2)
        ends   = df.index + (time_sep_days / 2)
        
        daily_stack = []
        for i in range(len(df)):
            if pd.isna(current_speed_series.iloc[i]): continue 
            
            s_date = starts.iloc[i].floor('D')
            e_date = ends.iloc[i].ceil('D')
            
            # For the trend line generation, we use the smoothed point value if available
            val_to_use = current_speed_series.iloc[i]
            try:
                if pd.notnull(processed_raw_series.loc[df.index[i]]):
                    val_to_use = processed_raw_series.loc[df.index[i]]
            except: pass

            date_rng = pd.date_range(start=s_date, end=e_date, freq='D')
            if not date_rng.empty:
                daily_stack.append(pd.DataFrame({'date': date_rng, 'speed': val_to_use}))

        if daily_stack:
            big_df = pd.concat(daily_stack)
            daily_ts = big_df.groupby('date')['speed'].median()
            daily_ts = daily_ts.reindex(full_idx)
        else:
            daily_ts = pd.Series(dtype=float, index=full_idx)

        # --- STEP 3: DAILY SMOOTHING & GAP RE-MASKING ---
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
                
                # Re-introduce gaps in the trend line
                daily_final[daily_ts_filled.isna()] = np.nan
        except Exception: 
            pass
            
        trend_on_dates = daily_final 

        output_data[key] = {
            # 'raw': Full length array (365 days), but mostly Nones. Points only on valid days.
            "raw": clean_nans(processed_raw_series), 
            # 'smoothed': Full length array (365 days), values everywhere except large gaps.
            "smoothed": clean_nans(trend_on_dates)              
        }

    return {
        "status": "success",
        "data": output_data
    }


def _load_input_to_gdf(loc_input):
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