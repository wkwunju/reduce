from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.db_storage import DatabaseStorage
from app.scheduler import scheduler
from app.dependencies.auth import get_current_user, get_current_user_optional
from app.models import User, JobStatus

router = APIRouter()

class JobCreateRequest(BaseModel):
    x_username: str
    frequency: str
    topics: List[str] = []
    language: Optional[str] = None
    email: Optional[str] = None
    notification_target_ids: Optional[List[int]] = None

class JobUpdateRequest(BaseModel):
    frequency: Optional[str] = None
    topics: Optional[List[str]] = None
    is_active: Optional[bool] = None
    language: Optional[str] = None
    email: Optional[str] = None
    notification_target_ids: Optional[List[int]] = None

@router.post("/")
def create_job(
    job_request: JobCreateRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new monitoring job (requires authentication)"""
    storage = DatabaseStorage(db)
    job = storage.create_job(
        x_username=job_request.x_username,
        frequency=job_request.frequency,
        topics=job_request.topics,
        language=job_request.language,
        email=job_request.email,  # Only use email when explicitly provided
        user_id=current_user.id,  # Associate job with current user
        notification_target_ids=job_request.notification_target_ids
    )
    
    # Schedule the job automatically
    scheduler.schedule_job(job["id"])
    
    return job

@router.get("/")
def get_all_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all jobs for the current user (requires authentication)"""
    storage = DatabaseStorage(db)
    return storage.get_user_jobs(current_user.id)

@router.get("/{job_id}")
def get_job(
    job_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific job (requires authentication and ownership)"""
    storage = DatabaseStorage(db)
    job = storage.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.get("status") == JobStatus.DELETED.value:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check ownership
    if job["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this job")
    
    return job

@router.patch("/{job_id}")
def update_job(
    job_id: int, 
    job_update: JobUpdateRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a monitoring job (requires authentication and ownership)"""
    storage = DatabaseStorage(db)
    
    # Check if job exists and user owns it
    existing_job = storage.get_job(job_id)
    if not existing_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if existing_job["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to update this job")
    if existing_job.get("status") == JobStatus.DELETED.value:
        raise HTTPException(status_code=404, detail="Job not found")
    
    update_data = {}
    if job_update.frequency is not None:
        update_data["frequency"] = job_update.frequency
    if job_update.topics is not None:
        update_data["topics"] = job_update.topics
    if job_update.is_active is not None:
        update_data["is_active"] = job_update.is_active
    if job_update.language is not None:
        update_data["language"] = job_update.language
    if job_update.email is not None:
        update_data["email"] = job_update.email
    if job_update.notification_target_ids is not None:
        update_data["notification_target_ids"] = job_update.notification_target_ids
    
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
def delete_job(
    job_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a monitoring job (requires authentication and ownership)"""
    storage = DatabaseStorage(db)
    
    # Check if job exists and user owns it
    existing_job = storage.get_job(job_id)
    if not existing_job:
        raise HTTPException(status_code=404, detail="Job not found")
    if existing_job.get("status") == JobStatus.DELETED.value:
        return {"message": "Job deleted successfully"}
    
    if existing_job["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to delete this job")
    
    if not storage.delete_job(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    scheduler.unschedule_job(job_id)
    return {"message": "Job deleted successfully"}

@router.get("/{job_id}/summaries")
def get_job_summaries(
    job_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all summaries for a job (requires authentication and ownership)"""
    storage = DatabaseStorage(db)
    job = storage.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check ownership
    if job["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this job's summaries")
    
    summaries = storage.get_summaries(job_id)
    return summaries

@router.get("/{job_id}/executions")
def get_job_executions(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all executions for a job (requires authentication and ownership)"""
    storage = DatabaseStorage(db)
    job = storage.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this job's executions")
    
    executions = storage.get_executions(job_id)
    return executions
