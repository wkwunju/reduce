from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.services.twitter_service import TwitterService
from app.services.llm_service import LLMService
from app.services.sendgrid_service import SendGridService
from app.services.db_storage import DatabaseStorage
from app.models import JobExecution, ExecutionStatus

class MonitoringService:
    def __init__(self):
        self.twitter_service = TwitterService()
        self.llm_service = LLMService()
        self.email_service = SendGridService()
    
    def run_job(self, job: Dict, db: Session) -> Dict:
        """
        Execute a monitoring job:
        1. Fetch tweets from X account
        2. Filter by topics
        3. Generate AI summary
        4. Store summary in memory
        """
        print("\n" + "=" * 80)
        print("[MONITORING SERVICE] Starting job execution")
        print(f"[MONITORING SERVICE] Job ID: {job.get('id')}")
        print(f"[MONITORING SERVICE] Username: @{job.get('x_username')}")
        print(f"[MONITORING SERVICE] Frequency: {job.get('frequency')}")
        print(f"[MONITORING SERVICE] Topics: {job.get('topics', [])}")
        print("=" * 80)
        
        # Create execution record for this task run
        execution = JobExecution(
            job_id=job["id"],
            status=ExecutionStatus.RUNNING
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)

        try:
            # Calculate time window based on frequency
            last_run_str = job.get("last_run")
            last_run = None
            if last_run_str:
                try:
                    last_run = datetime.fromisoformat(last_run_str.replace('Z', '+00:00'))
                    print(f"[MONITORING SERVICE] Last run: {last_run.isoformat()}")
                except:
                    print(f"[MONITORING SERVICE] Could not parse last_run: {last_run_str}")
                    pass
            
            since = self._get_since_time(job.get("frequency", "daily"), last_run)
            print(f"[MONITORING SERVICE] Fetching tweets since: {since.isoformat()}")
            
            # Fetch tweets
            print("[MONITORING SERVICE] Step 1: Fetching tweets...")
            tweets = self.twitter_service.get_user_tweets(
                username=job["x_username"],
                since=since,
                limit=50
            )
            print(f"[MONITORING SERVICE] ✅ Step 1 complete: {len(tweets)} tweets fetched")
            
            # Note: We don't filter by topics - instead we pass topics to LLM to focus on them
            topics = job.get("topics", [])
            if topics:
                print(f"[MONITORING SERVICE] Step 2: Topics of interest: {topics} (will be emphasized in LLM summary, not filtered)")
            else:
                print("[MONITORING SERVICE] Step 2: No specific topics - summarizing all tweets")
            
            # Generate AI summary with topic emphasis (no filtering)
            print(f"[MONITORING SERVICE] Step 3: Generating AI summary (emphasizing topics: {topics})...")
            time_range = f"since {since.isoformat()}"
            summary_result = self.llm_service.summarize_tweets(
                tweets,
                topics,
                x_username=job.get("x_username"),
                time_range=time_range
            )
            summary_text = summary_result.get("summary", "")
            usage = summary_result.get("usage", {})
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            print(f"[MONITORING SERVICE] ✅ Step 3 complete: Summary generated")
            
            # Store summary in database
            print("[MONITORING SERVICE] Step 4: Storing summary...")
            storage = DatabaseStorage(db)
            summary = storage.add_summary(
                job_id=job["id"],
                content=summary_text,
                raw_data={"tweets": tweets[:10], "count": len(tweets)},  # Only store first 10 tweets
                execution_id=execution.id,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
            print(f"[MONITORING SERVICE] ✅ Step 4 complete: Summary stored (ID: {summary.get('id')})")
            
            # Send email if configured
            email = job.get("email")
            if email:
                print(f"[MONITORING SERVICE] Step 5: Sending email to {email}...")
                email_sent = self.email_service.send_summary_email(
                    to_email=email,
                    x_username=job["x_username"],
                    summary=summary_text,
                    tweets_count=len(tweets),
                    topics=topics
                )
                if email_sent:
                    print(f"[MONITORING SERVICE] ✅ Step 5 complete: Email sent successfully")
                else:
                    print(f"[MONITORING SERVICE] ⚠️  Step 5: Email sending failed (check logs)")
            else:
                print("[MONITORING SERVICE] Step 5: Skipping email (no email configured for this job)")

            execution.status = ExecutionStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.tweets_fetched = len(tweets)
            db.commit()
            
            print("=" * 80 + "\n")
            return summary
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.completed_at = datetime.utcnow()
            execution.error_message = str(e)
            db.commit()
            raise
    
    def _get_since_time(self, frequency: str, last_run: Optional[datetime] = None) -> datetime:
        """
        Calculate the 'since' time based on frequency
        """
        now = datetime.utcnow()
        
        if last_run:
            # If job has run before, fetch tweets since last run
            return last_run
        
        # Otherwise, fetch based on frequency
        frequency_map = {
            "hourly": timedelta(hours=1),
            "every_6_hours": timedelta(hours=6),
            "every_12_hours": timedelta(hours=12),
            "daily": timedelta(days=1),
        }
        
        delta = frequency_map.get(frequency, timedelta(hours=1))
        return now - delta
