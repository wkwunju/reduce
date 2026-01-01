"""
Database storage service for jobs and summaries
"""
from sqlalchemy.orm import Session
from app.models import User, Job, Summary, JobExecution, NotificationTarget, JobStatus
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
                   email: Optional[str] = None, user_id: Optional[int] = None,
                   notification_target_ids: Optional[List[int]] = None,
                   language: Optional[str] = None) -> Dict:
        """Create a new monitoring job"""
        job = Job(
            user_id=user_id,
            x_username=x_username,
            frequency=frequency,
            topics=topics or [],
            language=language or "en",
            email=email,
            is_active=True
        )
        if notification_target_ids:
            targets = self.db.query(NotificationTarget).filter(
                NotificationTarget.id.in_(notification_target_ids),
                NotificationTarget.user_id == user_id
            ).all()
            job.notification_targets = targets
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
        query = query.filter(Job.status != JobStatus.DELETED)
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
        notification_target_ids = kwargs.pop("notification_target_ids", None)
        for key, value in kwargs.items():
            if value is not None and hasattr(job, key):
                setattr(job, key, value)
        if notification_target_ids is not None:
            targets = self.db.query(NotificationTarget).filter(
                NotificationTarget.id.in_(notification_target_ids),
                NotificationTarget.user_id == job.user_id
            ).all()
            job.notification_targets = targets
        
        job.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(job)
        return self._job_to_dict(job)
    
    def delete_job(self, job_id: int) -> bool:
        """Soft delete a job to preserve executions and summaries"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return False
        if job.status != JobStatus.DELETED:
            job.status = JobStatus.DELETED
            job.is_active = False
            job.updated_at = datetime.utcnow()
            self.db.commit()
        return True
    
    # Summary operations
    def add_summary(
        self,
        job_id: int,
        content: str,
        raw_data: Dict,
        execution_id: Optional[int] = None,
        input_tokens: int = 0,
        output_tokens: int = 0
    ) -> Dict:
        """Add a summary for a job"""
        summary = Summary(
            id=str(uuid.uuid4()),
            job_id=job_id,
            execution_id=execution_id,
            content=content,
            tweets_count=raw_data.get("count", 0),
            raw_data=raw_data
        )
        summary.input_tokens = input_tokens
        summary.output_tokens = output_tokens
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

    def get_executions(self, job_id: int, limit: int = 50) -> List[Dict]:
        """Get all executions for a job"""
        executions = self.db.query(JobExecution)\
            .filter(JobExecution.job_id == job_id)\
            .order_by(JobExecution.created_at.desc())\
            .limit(limit)\
            .all()
        return [self._execution_to_dict(e) for e in executions]
    
    # Helper methods
    def _job_to_dict(self, job: Job) -> Dict:
        """Convert Job model to dict"""
        notification_target_ids = [t.id for t in job.notification_targets] if job.notification_targets else []
        if not notification_target_ids and job.notification_target_id:
            notification_target_ids = [job.notification_target_id]
        return {
            "id": job.id,
            "user_id": job.user_id,
            "x_username": job.x_username,
            "frequency": job.frequency,
            "topics": job.topics or [],
            "language": job.language,
            "email": job.email,
            "is_active": job.is_active,
            "status": job.status.value if job.status else None,
            "notification_target_id": job.notification_target_id,
            "notification_target_ids": notification_target_ids,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "last_run": job.last_run.isoformat() if job.last_run else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None
        }

    def add_playground_summary(
        self,
        x_username: str,
        topics: List[str],
        hours_back: int,
        content: str,
        raw_data: Dict,
        input_tokens: int = 0,
        output_tokens: int = 0
    ) -> Dict:
        """Add a summary for playground runs"""
        summary = Summary(
            id=str(uuid.uuid4()),
            is_playground=True,
            x_username=x_username,
            topics=topics or [],
            hours_back=hours_back,
            content=content,
            tweets_count=raw_data.get("count", 0),
            raw_data=raw_data,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
        self.db.add(summary)
        self.db.commit()
        self.db.refresh(summary)
        return self._summary_to_dict(summary)
    
    def _summary_to_dict(self, summary: Summary) -> Dict:
        """Convert Summary model to dict"""
        return {
            "id": str(summary.id),
            "job_id": summary.job_id,
            "execution_id": summary.execution_id,
            "content": summary.content,
            "tweets_count": summary.tweets_count,
            "raw_data": summary.raw_data,
            "input_tokens": summary.input_tokens,
            "output_tokens": summary.output_tokens,
            "created_at": summary.created_at.isoformat() if summary.created_at else None
        }

    def _execution_to_dict(self, execution: JobExecution) -> Dict:
        """Convert JobExecution model to dict"""
        return {
            "id": execution.id,
            "job_id": execution.job_id,
            "status": execution.status.value if execution.status else None,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "tweets_fetched": execution.tweets_fetched,
            "error_message": execution.error_message,
            "created_at": execution.created_at.isoformat() if execution.created_at else None
        }
