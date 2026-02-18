from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import get_db, User, DownloadLog
from dependencies import get_current_user
from pydantic import BaseModel
from typing import Dict, List, Optional

router = APIRouter(prefix="/api/users", tags=["Users"])

# Response Schema
class UserProfile(BaseModel):
    email: str
    total_downloads: int
    total_volume_mb: float
    usage_breakdown: Dict[str, int]
    recent_downloads: list[dict]
    
# Schema for the incoming log request
class ActivityLogRequest(BaseModel):
    interaction_type: str # e.g. 'excel_download', 'image_download'
    filename: str
    file_size_mb: float
  
    
# logging endpoint
@router.post("/log", status_code=201)
def log_user_activity(
    activity: ActivityLogRequest, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Allows the frontend to report an action (like an Excel download) 
    so it appears in the user's history.
    """
    new_log = DownloadLog(
        user_id=current_user.id,
        interaction_type=activity.interaction_type,
        filename=activity.filename,
        file_size_mb=activity.file_size_mb
    )
    db.add(new_log)
    db.commit()
    return {"status": "logged"}



@router.get("/me", response_model=UserProfile)
def get_user_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    # A. Get Total Aggregates
    total_stats = db.query(
        func.count(DownloadLog.id).label("count"),
        func.sum(DownloadLog.file_size_mb).label("volume")
    ).filter(DownloadLog.user_id == current_user.id).first()
    
    total_count = total_stats.count or 0
    total_volume = total_stats.volume or 0.0

    # B. Get Breakdown by Type
    # We group by 'interaction_type' to see how many of each action the user did
    breakdown_query = db.query(
        DownloadLog.interaction_type,
        func.count(DownloadLog.id).label("count")
    ).filter(DownloadLog.user_id == current_user.id)\
     .group_by(DownloadLog.interaction_type).all()

    # Convert query result to a clean dictionary
    # Default keys ensure the UI always has something to show
    usage_map = {
        "cube_download": 0,
        "chart_export": 0,
        "data_download": 0,
        "map_click": 0
    }
    
    for row in breakdown_query:
        # If interaction_type is None (legacy logs), we treat it as 'cube_download'
        itype = row.interaction_type or "cube_download"
        usage_map[itype] = row.count

    # C. Get Recent History (Last 10)
    recent = db.query(DownloadLog).filter(DownloadLog.user_id == current_user.id)\
               .order_by(DownloadLog.timestamp.desc()).limit(10).all()
    
    recent_list = [
        {
            "filename": log.filename, 
            "date": log.timestamp,
            "size": log.file_size_mb,
            "type": log.interaction_type or "cube_download" # Pass type to UI
        }
        for log in recent
    ]
    
    return {
        "email": current_user.email,
        "total_downloads": total_count,
        "total_volume_mb": total_volume,
        "usage_breakdown": usage_map,
        "recent_downloads": recent_list
    }