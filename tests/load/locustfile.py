# File: web/tests/load/locustfile.py
from locust import HttpUser, between
from user_flows import StandardUserBehavior

class WebsiteUser(HttpUser):
    """
    A simulated user that spawns on the website.
    """
    # When a user finishes a task, they wait between 1 and 5 seconds
    # before doing the next one (simulating thinking time).
    wait_time = between(1, 5)
    
    # Assign the behaviors defined in user_flows.py
    tasks = [StandardUserBehavior]