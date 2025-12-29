"""
Database storage service for jobs and summaries
"""
from sqlalchemy.orm import Session
from app.models import User, Job, Summary
from typing import List, Optional, Dict
from datetime import datetime
import uuid

class DatabaseStorage:
    """Database storage for jobs and summaries"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # User operations
    def get_or_create_user(self, email: str) -> User:
        """Get existing user or create new one"""
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user
    
    # Job operations
    def create_job(self, x_username: str, frequency: str, topics: List[str], 
                   email: Optional[str] = None, user_id: Optional[int] = None) -> Dict:
        """Create a new monitoring job"""
        job = Job(
            user_id=user_id,
            x_username=x_username,
            frequency=frequency,
            topics=topics or [],
            email=email,
            is_active=True
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return self._job_to_dict(job)
    
    def get_job(self, job_id: int) -> Optional[Dict]:
        """Get a job by ID"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        return self._job_to_dict(job) if job else None
    
    def get_all_jobs(self, user_id: Optional[int] = None) -> List[Dict]:
        """Get all jobs, optionally filtered by user_id"""
        query = self.db.query(Job)
        if user_id is not None:
            query = query.filter(Job.user_id == user_id)
        jobs = query.all()
        return [self._job_to_dict(job) for job in jobs]
    
    def get_user_jobs(self, user_id: int) -> List[Dict]:
        """Get all jobs for a specific user"""
        return self.get_all_jobs(user_id=user_id)
    
    def update_job(self, job_id: int, **kwargs) -> Optional[Dict]:
        """Update a job"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None
        
        for key, value in kwargs.items():
            if value is not None and hasattr(job, key):
                setattr(job, key, value)
        
        job.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(job)
        return self._job_to_dict(job)
    
    def delete_job(self, job_id: int) -> bool:
        """Delete a job and its summaries"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if job:
            self.db.delete(job)
            self.db.commit()
            return True
        return False
    
    # Summary operations
    def add_summary(self, job_id: int, content: str, raw_data: Dict) -> Dict:
        """Add a summary for a job"""
        summary = Summary(
            id=str(uuid.uuid4()),
            job_id=job_id,
            content=content,
            tweets_count=raw_data.get("count", 0),
            raw_data=raw_data
        )
        self.db.add(summary)
        
        # Update job's last_run
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.last_run = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(summary)
        return self._summary_to_dict(summary)
    
    def get_summaries(self, job_id: int, limit: int = 50) -> List[Dict]:
        """Get all summaries for a job"""
        summaries = self.db.query(Summary)\
            .filter(Summary.job_id == job_id)\
            .order_by(Summary.created_at.desc())\
            .limit(limit)\
            .all()
        return [self._summary_to_dict(s) for s in summaries]
    
    # Helper methods
    def _job_to_dict(self, job: Job) -> Dict:
        """Convert Job model to dict"""
        return {
            "id": job.id,
            "user_id": job.user_id,
            "x_username": job.x_username,
            "frequency": job.frequency,
            "topics": job.topics or [],
            "email": job.email,
            "is_active": job.is_active,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "last_run": job.last_run.isoformat() if job.last_run else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None
        }
    
    def _summary_to_dict(self, summary: Summary) -> Dict:
        """Convert Summary model to dict"""
        return {
            "id": str(summary.id),
            "job_id": summary.job_id,
            "content": summary.content,
            "tweets_count": summary.tweets_count,
            "raw_data": summary.raw_data,
            "created_at": summary.created_at.isoformat() if summary.created_at else None
        }

