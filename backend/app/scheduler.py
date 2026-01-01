"""
Job Scheduler for XTrack
Automatically runs monitoring jobs based on configured frequency
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from app.database import SessionLocal
from app.services.db_storage import DatabaseStorage
from app.services.monitoring_service import MonitoringService

class JobScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.monitoring_service = MonitoringService()
        self.job_map = {}  # Maps job_id to scheduler job_id
        
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            print("[SCHEDULER] ✅ Scheduler started")
            # Schedule all active jobs
            self._schedule_all_jobs()
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("[SCHEDULER] Scheduler stopped")
    
    def _schedule_all_jobs(self):
        """Schedule all active jobs on startup"""
        db = SessionLocal()
        try:
            storage = DatabaseStorage(db)
            jobs = storage.get_all_jobs()
            for job in jobs:
                if job.get("is_active", True):
                    self.schedule_job(job["id"])
        finally:
            db.close()
    
    def schedule_job(self, job_id: int):
        """Schedule a job to run automatically"""
        db = SessionLocal()
        try:
            storage = DatabaseStorage(db)
            job = storage.get_job(job_id)
            if not job:
                print(f"[SCHEDULER] ⚠️  Job {job_id} not found")
                return
            
            if not job.get("is_active", True):
                print(f"[SCHEDULER] ⚠️  Job {job_id} is not active")
                return
        finally:
            db.close()
        
        # Remove existing schedule if any
        self.unschedule_job(job_id)
        
        # Get interval based on frequency
        frequency = job.get("frequency", "daily")
        interval_map = {
            "hourly": {"hours": 1},
            "every_6_hours": {"hours": 6},
            "every_12_hours": {"hours": 12},
            "daily": {"days": 1}
        }
        
        interval = interval_map.get(frequency, {"days": 1})
        
        # Schedule the job
        scheduler_job = self.scheduler.add_job(
            func=self._run_job,
            trigger=IntervalTrigger(**interval),
            args=[job_id],
            id=f"job_{job_id}",
            name=f"Monitor @{job.get('x_username')}",
            replace_existing=True
        )
        
        self.job_map[job_id] = f"job_{job_id}"
        
        print(f"[SCHEDULER] ✅ Scheduled job {job_id} (@{job.get('x_username')}) to run every {frequency}")
        print(f"[SCHEDULER] Next run: {scheduler_job.next_run_time}")
    
    def unschedule_job(self, job_id: int):
        """Remove a job from the schedule"""
        scheduler_job_id = self.job_map.get(job_id)
        if scheduler_job_id:
            try:
                self.scheduler.remove_job(scheduler_job_id)
                del self.job_map[job_id]
                print(f"[SCHEDULER] ⏸️  Unscheduled job {job_id}")
            except Exception as e:
                print(f"[SCHEDULER] ⚠️  Error unscheduling job {job_id}: {e}")
    
    def reschedule_job(self, job_id: int):
        """Reschedule a job (e.g., after frequency change)"""
        self.schedule_job(job_id)
    
    def _run_job(self, job_id: int):
        """Execute a scheduled job"""
        print("\n" + "=" * 80)
        print(f"[SCHEDULER] Running scheduled job {job_id}")
        print(f"[SCHEDULER] Time: {datetime.utcnow().isoformat()}")
        print("=" * 80)
        
        db = SessionLocal()
        try:
            storage = DatabaseStorage(db)
            job = storage.get_job(job_id)
            if not job:
                print(f"[SCHEDULER] ⚠️  Job {job_id} not found, unscheduling...")
                self.unschedule_job(job_id)
                return
            
            if not job.get("is_active", True):
                print(f"[SCHEDULER] ⚠️  Job {job_id} is not active, skipping...")
                return
            if job.get("status") == "deleted":
                print(f"[SCHEDULER] ⚠️  Job {job_id} is deleted, skipping...")
                return
            
            # Run the monitoring job
            summary = self.monitoring_service.run_job(job, db)
            
            print(f"[SCHEDULER] ✅ Job {job_id} completed successfully")
            print(f"[SCHEDULER] Summary ID: {summary.get('id')}")
            print("=" * 80 + "\n")
            
        except Exception as e:
            print(f"[SCHEDULER] ❌ Error running job {job_id}: {str(e)}")
            import traceback
            print(f"[SCHEDULER] Traceback:\n{traceback.format_exc()}")
            print("=" * 80 + "\n")
        finally:
            db.close()
    
    def get_scheduled_jobs(self):
        """Get list of currently scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None
            })
        return jobs

# Global scheduler instance
scheduler = JobScheduler()
