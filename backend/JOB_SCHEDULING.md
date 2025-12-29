# Job Scheduling in XTrack

## Overview

XTrack now includes **automatic job scheduling** that runs monitoring jobs based on the configured frequency.

## How It Works

### 1. **Scheduler Component** (`app/scheduler.py`)

The scheduler uses **APScheduler** (Advanced Python Scheduler) to run jobs automatically in the background.

### 2. **When Does It Run?**

- **On Server Startup**: All active jobs are automatically scheduled
- **When Creating a Job**: New jobs are immediately scheduled
- **When Updating a Job**: Jobs are rescheduled if frequency changes
- **When Pausing/Resuming**: Jobs are unscheduled/rescheduled accordingly

### 3. **Frequency Options**

- `hourly` - Every 1 hour
- `every_6_hours` - Every 6 hours
- `every_12_hours` - Every 12 hours
- `daily` - Every 24 hours

### 4. **What Happens During a Scheduled Run?**

1. Fetch tweets from X API
2. Generate AI summary using LLM
3. Store summary in memory
4. Send email (if configured)
5. Update `last_run` timestamp

## Running on Your Laptop

### ✅ Yes, It Works on Your Laptop!

The scheduler runs as a **background thread** within your backend server. As long as your backend is running, jobs will execute automatically.

### Requirements

1. **Backend server must be running**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **Your laptop must be awake** (not sleeping/hibernating)

3. **Internet connection** (for Twitter API and LLM API calls)

### Limitations of Running on Your Laptop

| Limitation | Impact | Solution |
|------------|--------|----------|
| **Laptop sleeps** | Jobs won't run while asleep | Keep laptop awake or deploy to server |
| **Server restarts** | Scheduler resets, may miss runs | Deploy to cloud with auto-restart |
| **Power off** | No jobs run when off | Use a cloud server (AWS, etc.) |
| **Memory only** | Data lost on restart | Will add database later |

## Production Deployment

For 24/7 monitoring, you should deploy to a cloud server:

### Recommended Options

1. **AWS EC2** (Simple, always-on virtual machine)
2. **AWS ECS** (Container-based, scalable)
3. **DigitalOcean Droplet** (Simple, affordable)
4. **Heroku** (Easy deployment, but worker dyno needed)

### What You'll Need for Production

1. **Always-on server** - Doesn't sleep like laptops
2. **Database** - Persistent storage (PostgreSQL)
3. **Process manager** - Keep server running (systemd, PM2, etc.)
4. **Auto-restart** - Restart on crashes
5. **Monitoring** - Track job executions

## Setup & Installation

### 1. Install APScheduler

```bash
cd backend
source venv/bin/activate
pip install apscheduler
```

Or it's already in the updated `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 2. Restart Backend Server

```bash
uvicorn app.main:app --reload
```

You should see:
```
[STARTUP] Starting job scheduler...
[SCHEDULER] ✅ Scheduler started
[STARTUP] ✅ Application started successfully
```

### 3. Create a Job

When you create a job via the frontend, you'll see:
```
[SCHEDULER] ✅ Scheduled job 1 (@elonmusk) to run every daily
[SCHEDULER] Next run: 2024-12-29 21:00:00.000000+00:00
```

## Monitoring Scheduled Jobs

### Check Logs

The scheduler logs all activities:

```
[SCHEDULER] Running scheduled job 1
[SCHEDULER] Time: 2024-12-28T20:00:00
================================================================================
[MONITORING SERVICE] Starting job execution
[MONITORING SERVICE] Job ID: 1
...
[SCHEDULER] ✅ Job 1 completed successfully
[SCHEDULER] Summary ID: abc-123
================================================================================
```

### Check Next Run Time

When a job is scheduled, it logs the next run time:
```
[SCHEDULER] Next run: 2024-12-29 21:00:00.000000+00:00
```

## Testing

### Test Without Waiting

You can still manually run jobs immediately:

1. **Via Frontend**: Click the ▶️ Play button on any job
2. **Via API**:
   ```bash
   curl -X POST http://localhost:8000/api/monitoring/jobs/1/run
   ```

This won't affect the schedule - the job will still run automatically at its scheduled time.

### Test Schedule Immediately

To test the scheduler without waiting hours:

1. **Temporarily change frequency to 1 minute** (modify `scheduler.py`):
   ```python
   interval_map = {
       "hourly": {"minutes": 1},  # Changed from hours=1
       ...
   }
   ```

2. **Create a job with "hourly" frequency**

3. **Wait 1 minute** - job will run automatically

4. **Change back to hours** for production use

## Pausing vs Deleting

### Pause (Deactivate)

- Unschedules the job
- Keeps job data and history
- Can resume later
- Click the ⏸ button in frontend

### Delete

- Completely removes job
- Deletes all summaries
- Cannot undo
- Click the 🗑️ button in frontend

## FAQ

### Q: Do jobs run while I'm not using the frontend?
**A:** Yes! As long as the backend server is running, jobs will execute automatically in the background.

### Q: What happens if my laptop restarts?
**A:** All scheduled jobs will be rescheduled when the backend starts up again. However, any runs that were supposed to happen during downtime will be missed.

### Q: Can I change the frequency of a running job?
**A:** Yes! Update the job frequency in the frontend, and it will automatically reschedule with the new frequency.

### Q: How do I know if a job ran successfully?
**A:** Check the "View Summaries" section - each successful run creates a new summary entry with timestamp.

### Q: What happens if a job fails?
**A:** The error is logged, and the job will try again at the next scheduled time. The scheduler continues running.

### Q: Can I run the same account on multiple frequencies?
**A:** Yes! Create multiple jobs for the same X account with different frequencies and topics.

## Next Steps

1. **Test locally** - Create jobs and verify they run
2. **Monitor logs** - Watch for scheduled executions
3. **Add database** - For persistent storage (coming later)
4. **Deploy to cloud** - For 24/7 monitoring

The scheduler is production-ready but runs on your laptop for now. When you're ready for 24/7 monitoring, we'll help you deploy to AWS or another cloud provider!

