# File: web/tests/load/user_flows.py
from locust import task, TaskSet
import random
import math

# Coordinates for testing (Greenland mini zarr approx limits)
LAT_MIN, LAT_MAX = 66.61, 67.57
LON_MIN, LON_MAX = -51.22, -48.75
REGION = "Greenland"

def deg2num(lat_deg, lon_deg, zoom):
    """
    Converts Lat/Lon to Web Mercator Tile coordinates (x, y).
    Standard logic used by OpenStreetMap/Google Maps.
    """
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

class StandardUserBehavior(TaskSet):
    """
    Defines the specific actions a standard user performs.
    """
    
    @task(1)
    def request_velocity_point(self):
        """
        Simulate clicking a point on the map.
        """
        lat = random.uniform(LAT_MIN, LAT_MAX)
        lon = random.uniform(LON_MIN, LON_MAX)
        
        # 1. Construct the Payload (matches your RoiRequest model in main.py)
        # Note: GIS usually expects [Longitude, Latitude] order
        payload = {
            "roi": [[lon, lat]], 
            "buffer": 500
        }
        
        # 2. Send POST request
        # We use the 'json' parameter which automatically formats the dict
        self.client.post(
            "/api/timeseries/json", 
            json=payload, 
            name="/api/timeseries/json" # Groups stats under this name
        )

    @task(5)
    def request_vector_tile(self):
        """
        Simulate panning the map and loading Vector Arrows.
        Weight: 5 (Map tiles are requested frequently)
        """
        # Pick a zoom level where arrows are actually visible/calculated
        z = random.randint(4, 8) 
        
        # Generate a random lat/lon inside your data bounds
        lat = random.uniform(LAT_MIN, LAT_MAX)
        lon = random.uniform(LON_MIN, LON_MAX)
        
        # Convert to valid tile coordinates
        x, y = deg2num(lat, lon, z)
        
        # Request the tile
        # URL: /api/tiles/{region}/vectors/{z}/{x}/{y}.png
        url = f"/api/tiles/{REGION}/vectors/{z}/{x}/{y}.png"
        
        self.client.get(
            url,
            name="/api/tiles/vectors" # Group all vector requests in stats
        )

    @task(10)
    def request_raster_tile(self):
        """
        Simulate panning the map and loading Raster Overlays (Speed, Trend, Count).
        Weight: 10 (These are the background layers, heavily requested)
        """
        # Randomly choose a layer type supported by your server
        layer = random.choice(["speed", "trend", "count"])
        z = random.randint(4, 8)
        
        lat = random.uniform(LAT_MIN, LAT_MAX)
        lon = random.uniform(LON_MIN, LON_MAX)
        x, y = deg2num(lat, lon, z)
        
        # URL: /api/tiles/{region}/{layer_type}/{z}/{x}/{y}.png
        url = f"/api/tiles/{REGION}/{layer}/{z}/{x}/{y}.png"
        
        self.client.get(
            url,
            name=f"/api/tiles/raster/[layer]" # Group raster requests
        )
        
    #@task(1)
    #def view_homepage(self):
    #    """Simulate loading the landing page"""
    #    self.client.get("/")

    #@task(1)
    #def view_documentation(self):
    #    """Simulate reading the docs"""
    #    self.client.get("/documentation")