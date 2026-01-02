from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.db_storage import DatabaseStorage
from app.services.monitoring_service import MonitoringService
from app.services.twitter_service import TwitterService
from app.services.llm_service import LLMService
from app.services.sendgrid_service import SendGridService

router = APIRouter()
monitoring_service = MonitoringService()

class TestRequest(BaseModel):
    x_username: str
    topics: Optional[List[str]] = []
    hours_back: Optional[int] = 24  # Default to last 24 hours
    email: Optional[str] = None  # Optional email to send test results
    language: Optional[str] = None

class SendEmailRequest(BaseModel):
    email: str
    summary_id: Optional[str] = None  # If provided, send specific summary

@router.post("/test")
def test_monitoring(
    test_request: TestRequest,
    db: Session = Depends(get_db)
):
    """Test function to execute monitoring immediately with a time range"""
    print("\n" + "=" * 80)
    print("[API ENDPOINT] /api/monitoring/test - Starting test")
    print(f"[API ENDPOINT] Request data: username={test_request.x_username}, hours_back={test_request.hours_back}, topics={test_request.topics}, language={test_request.language}")
    print("=" * 80)
    
    try:
        print("[API ENDPOINT] Initializing services...")
        twitter_service = TwitterService()
        llm_service = LLMService()
        print("[API ENDPOINT] ✅ Services initialized")
        
        # Calculate time range
        until_time = datetime.utcnow()
        since_time = until_time - timedelta(hours=test_request.hours_back)
        print(f"[API ENDPOINT] Time range: {since_time.isoformat()} to {until_time.isoformat()}")
        
        # Fetch tweets (this may take time due to rate limiting)
        print("[API ENDPOINT] Step 1: Fetching tweets from Twitter API...")
        tweets = twitter_service.get_user_tweets(
            username=test_request.x_username,
            since=since_time,
            limit=50
        )
        print(f"[API ENDPOINT] ✅ Step 1 complete: Fetched {len(tweets)} tweets")
        
        # Note: We don't filter by topics - instead we pass topics to LLM to focus on them
        if test_request.topics:
            print(f"[API ENDPOINT] Step 2: Topics of interest: {test_request.topics} (will be emphasized in LLM summary, not filtered)")
        else:
            print("[API ENDPOINT] Step 2: No specific topics - summarizing all tweets")
        
        # Generate AI summary with topic emphasis
        provider_name = llm_service.provider if hasattr(llm_service, 'provider') else 'LLM'
        print(f"[API ENDPOINT] Step 3: Generating AI summary with {provider_name} (emphasizing topics: {test_request.topics})...")
        time_range = f"last {test_request.hours_back} hours"
        summary_result = llm_service.summarize_tweets(
            tweets,
            test_request.topics,
            x_username=test_request.x_username,
            time_range=time_range,
            language=test_request.language
        )
        summary_text = summary_result.get("summary", "")
        usage = summary_result.get("usage", {}) or {}
        print(f"[API ENDPOINT] ✅ Step 3 complete: Summary generated ({len(summary_text)} characters)")
        
        # Send email if provided
        email_sent = False
        if test_request.email:
            print(f"[API ENDPOINT] Step 4: Sending email to {test_request.email}...")
            email_service = SendGridService()
            email_sent = email_service.send_summary_email(
                to_email=test_request.email,
                x_username=test_request.x_username,
                summary=summary_text,
                tweets_count=len(tweets),
                topics=test_request.topics,
                headline=summary_result.get("headline")
            )
            if email_sent:
                print(f"[API ENDPOINT] ✅ Step 4 complete: Email sent successfully")
            else:
                print(f"[API ENDPOINT] ⚠️  Step 4: Email sending failed")
        
        storage = DatabaseStorage(db)
        playground_summary = storage.add_playground_summary(
            x_username=test_request.x_username,
            topics=test_request.topics or [],
            hours_back=test_request.hours_back or 24,
            content=summary_text,
            raw_data={"count": len(tweets)},
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0)
        )

        result = {
            "x_username": test_request.x_username,
            "topics": test_request.topics,
            "hours_back": test_request.hours_back,
            "language": test_request.language,
            "tweets_found": len(tweets),
            "summary": summary_text,
            "summary_id": playground_summary.get("id"),
            "tweets": tweets[:10],  # Return first 10 tweets for preview
            "since_time": since_time.isoformat(),
            "until_time": until_time.isoformat(),
            "email_sent": email_sent
        }
        
        print("=" * 80)
        print("[API ENDPOINT] ✅ Test completed successfully")
        print(f"[API ENDPOINT] Final result: {len(tweets)} tweets, summary length: {len(summary_text)} chars")
        if test_request.email:
            print(f"[API ENDPOINT] Email sent: {email_sent}")
        print("=" * 80 + "\n")
        
        return result
    except Exception as e:
        error_message = str(e)
        print("=" * 80)
        print(f"[API ENDPOINT] ❌ ERROR: {error_message}")
        import traceback
        print(f"[API ENDPOINT] Traceback:\n{traceback.format_exc()}")
        print("=" * 80 + "\n")
        
        # Provide user-friendly error messages
        if "Rate limit" in error_message or "429" in error_message:
            raise HTTPException(
                status_code=429, 
                detail="Twitter API rate limit exceeded. Please wait at least 5 seconds between requests and try again."
            )
        raise HTTPException(status_code=500, detail=f"Error testing: {error_message}")

@router.post("/jobs/{job_id}/run")
def run_job_manually(job_id: int, db: Session = Depends(get_db)):
    """Manually trigger a monitoring job"""
    storage = DatabaseStorage(db)
    job = storage.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.get("is_active", True):
        raise HTTPException(status_code=400, detail="Job is not active")
    
    try:
        summary = monitoring_service.run_job(job, db)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running job: {str(e)}")

@router.post("/jobs/{job_id}/summaries/send-email")
def send_summary_email(job_id: int, email_request: SendEmailRequest, db: Session = Depends(get_db)):
    """Send an existing summary via email without regenerating content"""
    print("\n" + "=" * 80)
    print(f"[API ENDPOINT] /api/monitoring/jobs/{job_id}/summaries/send-email")
    print(f"[API ENDPOINT] Email: {email_request.email}")
    print(f"[API ENDPOINT] Summary ID: {email_request.summary_id}")
    print("=" * 80)
    
    try:
        storage = DatabaseStorage(db)
        
        # Get job
        job = storage.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get summaries
        summaries = storage.get_summaries(job_id)
        if not summaries:
            raise HTTPException(status_code=404, detail="No summaries found for this job")
        
        # Find the summary to send
        if email_request.summary_id:
            # Find specific summary by ID
            summary = next((s for s in summaries if s.get("id") == email_request.summary_id), None)
            if not summary:
                raise HTTPException(status_code=404, detail="Summary not found")
        else:
            # Use the latest summary
            summary = summaries[-1]
        
        print(f"[API ENDPOINT] Sending summary {summary.get('id')} via email...")
        
        # Send email
        email_sent = email_service.send_summary_email(
            to_email=email_request.email,
            x_username=job.get("x_username"),
            summary=summary.get("content"),
            tweets_count=summary.get("raw_data", {}).get("count", 0),
            topics=job.get("topics", [])
        )
        
        if email_sent:
            print(f"[API ENDPOINT] ✅ Email sent successfully to {email_request.email}")
            return {
                "message": "Email sent successfully",
                "email": email_request.email,
                "summary_id": summary.get("id"),
                "email_sent": True
            }
        else:
            print(f"[API ENDPOINT] ⚠️  Email sending failed or disabled")
            return {
                "message": "Email service not configured or failed",
                "email": email_request.email,
                "summary_id": summary.get("id"),
                "email_sent": False
            }
    
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        print("=" * 80)
        print(f"[API ENDPOINT] ❌ ERROR: {error_message}")
        import traceback
        print(f"[API ENDPOINT] Traceback:\n{traceback.format_exc()}")
        print("=" * 80 + "\n")
        raise HTTPException(status_code=500, detail=f"Error sending email: {error_message}")
