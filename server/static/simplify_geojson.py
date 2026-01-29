import geopandas as gpd
import os

def simplify_geojson(input_file, output_file, tolerance):
    """
    Reads a GeoJSON, simplifies the geometry, and saves it.
    
    :param input_file: Path to source file
    :param output_file: Path to destination file
    :param tolerance: The simplification tolerance. 
                      - If your data is in Lat/Lon (EPSG:4326), this is in DEGREES.
                        (e.g., 0.001 is roughly 111 meters)
                      - If your data is in Meters (Polar Stereographic), this is in METERS.
                        (e.g., 100 is 100 meters)
    """
    print(f"--- Processing {input_file} ---")
    
    # 1. Check if file exists
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found.")
        return

    # 2. Load the data
    print("Loading data... (this might take a moment)")
    gdf = gpd.read_file(input_file)
    
    original_points = gdf.geometry.apply(lambda x: len(x.exterior.coords) if x.geom_type == 'Polygon' else len(x.coords) if x.geom_type == 'LineString' else 0).sum()
    
    # 3. Simplify
    # preserve_topology=True is slower but ensures polygons don't overlap themselves
    print(f"Simplifying with tolerance: {tolerance}...")
    gdf['geometry'] = gdf['geometry'].simplify(tolerance, preserve_topology=True)
    
    # 4. Save to new file
    print(f"Saving to {output_file}...")
    gdf.to_file(output_file, driver='GeoJSON')
    
    # 5. Print Stats
    orig_size_mb = os.path.getsize(input_file) / (1024 * 1024)
    new_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    
    print(f"Done!")
    print(f"Original Size: {orig_size_mb:.2f} MB")
    print(f"New Size:      {new_size_mb:.2f} MB")
    print(f"Reduction:     {100 - (new_size_mb/orig_size_mb*100):.1f}%")
    print("\n")

if __name__ == "__main__":
    # CONFIGURATION
    # ---------------------------------------------------------
    # TOLERANCE EXPLAINED:
    # If your GeoJSON is in Lat/Lon (WGS84), 0.01 is ~1km, 0.001 is ~100m.
    # Start with 0.001. If the file is still too big, try 0.005 or 0.01.
    # If the lines look "blocky", lower the number.
    TOLERANCE = 0.005 

    # PROCESS FILES
    # ---------------------------------------------------------
    
    # 1. Ice Edge
    simplify_geojson(
        input_file="iceedge_merged.geojson", 
        output_file="iceedge_merged_simple.geojson", 
        tolerance=TOLERANCE
    )

    # 2. Grounding Line
    #simplify_geojson(
    #    input_file="apgroundingline.geojson", 
    #    output_file="apgroundingline_simple.geojson", 
    #    tolerance=TOLERANCE
    #)
	