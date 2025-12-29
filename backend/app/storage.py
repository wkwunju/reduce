"""
In-memory storage for jobs and summaries.
This will be replaced with a database in a later stage.
"""
from typing import Dict, List, Optional
from datetime import datetime
from uuid import uuid4

class InMemoryStorage:
    """Simple in-memory storage for jobs and summaries"""
    
    def __init__(self):
        self.jobs: Dict[int, Dict] = {}
        self.summaries: Dict[int, List[Dict]] = {}  # job_id -> list of summaries
        self.next_job_id = 1
    
    def create_job(self, x_username: str, frequency: str, topics: List[str], email: Optional[str] = None) -> Dict:
        """Create a new monitoring job"""
        job_id = self.next_job_id
        self.next_job_id += 1
        
        job = {
            "id": job_id,
            "x_username": x_username,
            "frequency": frequency,
            "topics": topics or [],
            "email": email,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "last_run": None
        }
        
        self.jobs[job_id] = job
        self.summaries[job_id] = []
        return job
    
    def get_job(self, job_id: int) -> Optional[Dict]:
        """Get a job by ID"""
        return self.jobs.get(job_id)
    
    def get_all_jobs(self) -> List[Dict]:
        """Get all jobs"""
        return list(self.jobs.values())
    
    def update_job(self, job_id: int, **kwargs) -> Optional[Dict]:
        """Update a job"""
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        for key, value in kwargs.items():
            if value is not None:
                job[key] = value
        
        return job
    
    def delete_job(self, job_id: int) -> bool:
        """Delete a job and its summaries"""
        if job_id in self.jobs:
            del self.jobs[job_id]
            if job_id in self.summaries:
                del self.summaries[job_id]
            return True
        return False
    
    def add_summary(self, job_id: int, content: str, raw_data: Dict) -> Dict:
        """Add a summary for a job"""
        summary = {
            "id": str(uuid4()),
            "job_id": job_id,
            "content": content,
            "raw_data": raw_data,
            "created_at": datetime.utcnow().isoformat()
        }
        
        if job_id not in self.summaries:
            self.summaries[job_id] = []
        
        self.summaries[job_id].append(summary)
        
        # Update job's last_run
        if job_id in self.jobs:
            self.jobs[job_id]["last_run"] = datetime.utcnow().isoformat()
        
        return summary
    
    def get_summaries(self, job_id: int) -> List[Dict]:
        """Get all summaries for a job"""
        return self.summaries.get(job_id, [])

# Global storage instance
storage = InMemoryStorage()

