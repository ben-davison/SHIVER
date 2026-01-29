# File: web/tests/load/user_flows.py
from locust import task, TaskSet
import random

# Coordinates for testing (Greenland mini zarr approx limits)
LAT_MIN, LAT_MAX = 66.61, 67.57
LON_MIN, LON_MAX = -51.22, -48.75

class StandardUserBehavior(TaskSet):
    """
    Defines the specific actions a standard user performs.
    """
    
    @task
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

    #@task(1)
    #def view_homepage(self):
    #    """Simulate loading the landing page"""
    #    self.client.get("/")

    #@task(1)
    #def view_documentation(self):
    #    """Simulate reading the docs"""
    #    self.client.get("/documentation")