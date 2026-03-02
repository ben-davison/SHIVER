from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List
import os
from sqlalchemy.orm import Session
from models import User, get_db, SessionLocal, DownloadLog

# IMPORTS
# Helper functions
from utils.extract_zarr_cube import generate_netcdf_cube, estimate_cube_size
from utils.email import send_cube_ready_email
# Imports for authentication
from models import User
from dependencies import get_current_user, LARGE_FILE_THRESHOLD_MB

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
    
async def process_large_cube(payload: CubeRequest, user_email: str, target_freq: str, origin_url: str):
    """
    This runs in the background AFTER the response is sent to the user.
    """
    try:
        print(f"⏳ Background processing started for {user_email}...")
        
        # 1. Generate the file (This takes time)
        target_freq = FREQ_MAP[payload.frequency.lower()]
        file_path, region = generate_netcdf_cube(
            geojson_geometry=payload.roi_geojson,
            date_range=(payload.date_start, payload.date_end),
            variables=payload.variables,
            frequency=target_freq,
            max_size_mb=50 # Allow larger limits for background jobs
        )
        
        # 2. Generate a Download Link
        # In a real app, you'd upload this file to S3/Cloud Storage and get a URL.
        # For now, we assume the file stays on the server.
        filename = os.path.basename(file_path)
        clean_base = origin_url.rstrip("/")
        download_link = f"{clean_base}/static/exports/{filename}"
        
        # LOGGING TO DB
        # We open a dedicated session for this background task
        db = SessionLocal() 
        try:
            user = db.query(User).filter(User.email == user_email).first()
            if user:
                # Calculate actual size
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                
                log = DownloadLog(
                    user_id=user.id,
                    interaction_type="cube_download",
                    filename=os.path.basename(file_path),
                    file_size_mb=size_mb
                )
                db.add(log)
                db.commit()
        finally:
            db.close() # close manual session
        
        # 3. Send Email
        await send_cube_ready_email(user_email, download_link, region)
        print(f"✅ Background job done. Email sent to {user_email}")

    except Exception as e:
        print(f"❌ Background job failed: {e}")
        # Ideally, send a "Failed" email here

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
        
        # 2. ESTIMATE SIZE
        estimated_mb = estimate_cube_size(
            geojson_geometry=payload.roi_geojson,
            date_range=(payload.date_start, payload.date_end),
            variables=payload.variables,
            frequency=target_freq
        )
        print(f"🧐 Estimated Size: {estimated_mb:.2f} MB")
        
        
        # 3. DECISION LOGIC
        if estimated_mb > LARGE_FILE_THRESHOLD_MB:
            # === PATH A: LARGE FILE (Email) ===
            
            # Capture the current base URL 
            current_origin = str(request.base_url)
            
            # Queue the background task
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
                    "message": f"File is large ({estimated_mb:.0f} MB). We will email {current_user.email} when ready.",
                    "type": "email_notification"
                }
            )
        
        else:
            # === PATH B: SMALL FILE (Direct Download) ===
            
            # Generate immediately
            file_path, region = generate_netcdf_cube(
                geojson_geometry=payload.roi_geojson,
                date_range=(payload.date_start, payload.date_end),
                variables=payload.variables,
                frequency=target_freq,
                max_size_mb=LARGE_FILE_THRESHOLD_MB + 5
            )
            
            filename = f"{region}_{payload.frequency}_{payload.date_start}_{payload.date_end}.nc"
            
            # Cleanup
            def cleanup():
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            background_tasks.add_task(cleanup)
            
            # LOGGING TO DB
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            log = DownloadLog(
                user_id=current_user.id,
                interaction_type="cube_download",
                filename=filename,
                file_size_mb=size_mb
            )
            db.add(log)
            db.commit()
            
            return FileResponse(
                path=file_path, 
                filename=filename, 
                media_type='application/x-netcdf'
            )

    except ValueError as e:
        # Catch explicit size errors from generate_netcdf_cube
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
        