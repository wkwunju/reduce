from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.db_storage import DatabaseStorage
from app.scheduler import scheduler

router = APIRouter()

class JobCreateRequest(BaseModel):
    x_username: str
    frequency: str
    topics: List[str] = []
    email: Optional[str] = None

class JobUpdateRequest(BaseModel):
    frequency: Optional[str] = None
    topics: Optional[List[str]] = None
    is_active: Optional[bool] = None
    email: Optional[str] = None

@router.post("/")
def create_job(job_request: JobCreateRequest, db: Session = Depends(get_db)):
    """Create a new monitoring job"""
    storage = DatabaseStorage(db)
    job = storage.create_job(
        x_username=job_request.x_username,
        frequency=job_request.frequency,
        topics=job_request.topics,
        email=job_request.email
    )
    
    # Schedule the job automatically
    scheduler.schedule_job(job["id"])
    
    return job

@router.get("/")
def get_all_jobs(db: Session = Depends(get_db)):
    """Get all jobs"""
    storage = DatabaseStorage(db)
    return storage.get_all_jobs()

@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job"""
    storage = DatabaseStorage(db)
    job = storage.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.patch("/{job_id}")
def update_job(job_id: int, job_update: JobUpdateRequest, db: Session = Depends(get_db)):
    """Update a monitoring job"""
    storage = DatabaseStorage(db)
    
    update_data = {}
    if job_update.frequency is not None:
        update_data["frequency"] = job_update.frequency
    if job_update.topics is not None:
        update_data["topics"] = job_update.topics
    if job_update.is_active is not None:
        update_data["is_active"] = job_update.is_active
    if job_update.email is not None:
        update_data["email"] = job_update.email
    
    job = storage.update_job(job_id, **update_data)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Reschedule if frequency changed or reactivated
    if job_update.frequency is not None or (job_update.is_active is True):
        scheduler.schedule_job(job_id)
    # Unschedule if deactivated
    elif job_update.is_active is False:
        scheduler.unschedule_job(job_id)
    
    return job

@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a monitoring job"""
    storage = DatabaseStorage(db)
    
    # Unschedule first
    scheduler.unschedule_job(job_id)
    
    if not storage.delete_job(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted successfully"}

@router.get("/{job_id}/summaries")
def get_job_summaries(job_id: int, db: Session = Depends(get_db)):
    """Get all summaries for a job"""
    storage = DatabaseStorage(db)
    job = storage.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    summaries = storage.get_summaries(job_id)
    return summaries

