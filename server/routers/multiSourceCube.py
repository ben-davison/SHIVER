from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from models import User, get_db, SessionLocal, DownloadLog
from shapely.geometry import shape
import os
import zipfile
import functools
import asyncio

# Helper functions
from utils.extract_multi_zarr_cube import generate_multi_netcdf_cube
from utils.email import send_cube_ready_email, send_cube_failed_email, send_dev_error_email
from dependencies import get_current_user, check_daily_cube_limit

router = APIRouter(prefix="/api/multiSourceCube", tags=["Multi Data Cubes"])

class MultiCubeRequest(BaseModel):
    roi_geojson: dict
    date_start: str
    date_end: str
    variables: List[str] = ["speed", "speed_error"]
    sources: List[str] = []
    mode: str = "multi"
    
    
def process_multi_cube(payload: MultiCubeRequest, user_email: str, origin_url: str):
    # 1. Pre-determine the region for the email
    try:
        user_shape = shape(payload.roi_geojson)
        region = "Antarctica" if user_shape.centroid.y < 0 else "Greenland"
    except Exception:
        region = "Unknown Region"
    
    try:
        print(f"Background processing multi-source cube for {user_email}...")
        
        file_path, region, citation_text, csv_text = generate_multi_netcdf_cube(
            geojson_geometry=payload.roi_geojson,
            date_range=(payload.date_start, payload.date_end),
            sources=payload.sources,
            variables=payload.variables
        )
        
        # 2 Create ZIP archive
        nc_filename = os.path.basename(file_path)
        zip_filename = nc_filename.replace('.nc', '.zip')
        zip_file_path = file_path.replace('.nc', '.zip')
        
        print(f"Compressing into {zip_filename}...")
        
        # Write both files into the zip archive
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 1. Add the NetCDF file
            zipf.write(file_path, arcname=nc_filename)
            # 2. Add the citations text file and summary csv dynamically from the string
            zipf.writestr("citations_and_usage.txt", citation_text)
            zipf.writestr("citations_summary.csv", csv_text)
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Warning: Could not delete raw .nc file {file_path}: {e}")
        
        # Update the download link to point to the new zip file
        clean_base = origin_url.rstrip("/")
        download_link = f"{clean_base}/static/exports/{zip_filename}"
        
        db = SessionLocal() 
        try:
            user = db.query(User).filter(User.email == user_email).first()
            if user:
                size_mb = os.path.getsize(zip_file_path) / (1024 * 1024)
                log = DownloadLog(
                    user_id=user.id,
                    interaction_type="multi_cube_download",
                    filename=zip_filename,
                    file_size_mb=size_mb
                )
                db.add(log)
                db.commit()
        finally:
            db.close()
        
        asyncio.run(send_cube_ready_email(user_email, download_link, region))
        print(f"Background multi-source job done. Email sent to {user_email}")

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
            
            # Extract the raw payload data cleanly
            request_details = payload.model_dump()
            
            # Fire off the dev email with the real traceback and request data
            asyncio.run(send_dev_error_email(
                user_email=user_email, 
                region=region, 
                raw_error=str(e), 
                payload_data=request_details
            ))
            
        asyncio.run(send_cube_failed_email(user_email, region, friendly_msg))


@router.post("/download")
def download_multi_cube(
    request: Request, 
    payload: MultiCubeRequest, 
    background_tasks: BackgroundTasks, 
    current_user: User = Depends(get_current_user),
    rate_limit_passed: bool = Depends(check_daily_cube_limit) 
): 
    try:
        current_origin = str(request.base_url)
        
        # Always run as a background task
        background_tasks.add_task(
            process_multi_cube, 
            payload, 
            current_user.email, 
            current_origin
        )
        
        return JSONResponse(
            status_code=202,
            content={
                "message": f"Multi-source data extraction started. We will email {current_user.email} when ready.",
                "type": "email_notification"
            }
        )

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))