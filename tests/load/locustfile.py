# File: web/tests/load/locustfile.py
from locust import HttpUser, between
from user_flows import StandardUserBehavior

class WebsiteUser(HttpUser):
    """
    A simulated user that spawns on the website.
    """
    # Simulate a user viewing the map, clicking, and waiting for layers to render
    wait_time = between(19, 30) 
    
    tasks = [StandardUserBehavior]