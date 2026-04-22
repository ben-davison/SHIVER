from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List
import os
import zipfile
from sqlalchemy.orm import Session
from models import User, get_db, SessionLocal, DownloadLog
from shapely.geometry import shape

# IMPORTS
# Helper functions
from utils.extract_zarr_cube import generate_netcdf_cube
from utils.email import send_cube_ready_email, send_cube_failed_email
# Imports for authentication
from models import User
from dependencies import get_current_user

# Create the router
router = APIRouter(prefix="/api/cube", tags=["Data Cubes"])

# Define the mapping of aggregration frequency names
FREQ_MAP = {
    "native": "native",
    "monthly": "MS",   # Month Start
    "quarterly": "QS", # Quarter Start
    "annual": "AS"     # Year Start
}

class CubeRequest(BaseModel):
    roi_geojson: dict
    date_start: str
    date_end: str
    variables: List[str] = ["s_filt", "u_filt", "v_filt", "s_raw", "u_raw", "v_raw"]
    frequency: str = "native"
    mode: str = "single"
    
async def process_large_cube(payload: CubeRequest, user_email: str, target_freq: str, origin_url: str):
    """
    This runs in the background AFTER the response is sent to the user.
    """
    
    # 1. Pre-determine the region for the email
    try:
        user_shape = shape(payload.roi_geojson)
        region = "Antarctica" if user_shape.centroid.y < 0 else "Greenland"
    except Exception:
        region = "Unknown Region"
        
        
    try:
        print(f"Background processing started for {user_email}...")
        
        # 1. Generate the file (This takes time)
        target_freq = FREQ_MAP[payload.frequency.lower()]
        file_path, region, citation_text, csv_text = generate_netcdf_cube(
            geojson_geometry=payload.roi_geojson,
            date_range=(payload.date_start, payload.date_end),
            variables=payload.variables,
            frequency=target_freq
        )
        
        # Create ZIP archive
        nc_filename = os.path.basename(file_path)
        zip_filename = nc_filename.replace('.nc', '.zip')
        zip_file_path = file_path.replace('.nc', '.zip')
        
        print(f"Compressing into {zip_filename}...")
        
        # Write both files into the zip archive
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file_path, arcname=nc_filename)
            zipf.writestr("citations_and_usage.txt", citation_text)
            zipf.writestr("citations_summary.csv", csv_text)
            
        # Clean up the raw .nc file to save server space
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Warning: Could not delete raw .nc file {file_path}: {e}")
        
        # 2. Generate a Download Link
        clean_base = origin_url.rstrip("/")
        download_link = f"{clean_base}/static/exports/{zip_filename}"
        
        # LOGGING TO DB
        # open a dedicated session for background task
        db = SessionLocal() 
        try:
            user = db.query(User).filter(User.email == user_email).first()
            if user:
                # Calculate and record actual size
                size_mb = os.path.getsize(zip_file_path) / (1024 * 1024)
                log = DownloadLog(
                    user_id=user.id,
                    interaction_type="cube_download",
                    filename=zip_filename,
                    file_size_mb=size_mb
                )
                db.add(log)
                db.commit()
        finally:
            db.close() # close manual session
        
        # 3. Send Email
        await send_cube_ready_email(user_email, download_link, region)
        print(f"Background job done. Email sent to {user_email}")

    except Exception as e:
        print(f"Background job failed: {e}")
        
        raw_error = str(e).lower()
        
        # 2. Sanitize the error message for the user
        if "too large" in raw_error or "memory" in raw_error or "killed" in raw_error:
            friendly_msg = "The requested area or time period contained too much data to process. Please try drawing a smaller region."
        elif "empty" in raw_error or "no data" in raw_error or "bounds" in raw_error:
            friendly_msg = "No satellite data was found inside the exact region and time period you selected."
        elif "region not found" in raw_error:
            friendly_msg = "The drawn region falls outside of the supported boundaries for Greenland and Antarctica."
        else:
            friendly_msg = "An unexpected technical issue occurred while packaging your NetCDF file. Our development team has been notified."
            
        await send_cube_failed_email(user_email, region, friendly_msg)
        


@router.post("/download")
def download_cube(request: Request, payload: CubeRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        
        # Validate and Translate the frequency
        req_freq = payload.frequency.lower() # handle "Monthly" vs "monthly"
        
        # Check a valid frequency was provided
        if req_freq not in FREQ_MAP:
             raise HTTPException(
                 status_code=400, 
                 detail=f"Invalid frequency. Choose from: {list(FREQ_MAP.keys())}"
             )
        
        target_freq = FREQ_MAP[req_freq]

        # Queue the background task
        current_origin = str(request.base_url)
        background_tasks.add_task(
            process_large_cube, 
            payload, 
            current_user.email, 
            target_freq,
            current_origin
        )
            
        # Return immediately
        return JSONResponse(
            status_code=202,
            content={
                "message": f"Data extraction started. We will email {current_user.email} when ready.",
                "type": "email_notification"
            }
        )
        
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
        