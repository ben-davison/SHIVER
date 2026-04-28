# File: web/tests/resources/monitor.py
import psutil
import time
import csv
import os
from datetime import datetime

# CONFIGURATION
PROCESS_NAME = "python" # "python" for Flask/Django, "node" for Node.js
# Save results to the sibling "results" directory
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "../results/server_stats.csv")

def get_process_memory():
    total_mem = 0
    # Iterate over all running processes
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            if PROCESS_NAME in proc.info['name']:
                total_mem += proc.info['memory_info'].rss 
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return total_mem / (1024 * 1024) # Convert Bytes to MB

print(f"--- SERVER MONITOR STARTED ---")
print(f"Tracking process: {PROCESS_NAME}")
print(f"Saving data to: {os.path.abspath(OUTPUT_FILE)}")
print("Press Ctrl+C to stop.")

# Ensure directory exists
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

with open(OUTPUT_FILE, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "RAM_Usage_MB", "CPU_Percent"])

    try:
        while True:
            mem = get_process_memory()
            cpu = psutil.cpu_percent(interval=None) # System CPU
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] RAM: {mem:.2f} MB | CPU: {cpu}%")
            
            writer.writerow([timestamp, mem, cpu])
            time.sleep(1) # Log every second
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")