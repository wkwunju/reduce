# Database Migration Guide

## Overview

This guide explains the database schema changes to support:
1. User email verification status (already implemented via `UserStatus`)
2. Job execution history tracking
3. Playground run support in summaries

## Schema Changes

### 1. User Verification Status ✅ (Already Implemented)

The `users` table already has a `status` column with the following values:
- `UNVERIFIED`: Email not verified yet (default for new registrations)
- `ACTIVE`: Email verified, normal active user
- `SUSPENDED`: Account suspended/banned

### 2. New Table: `job_executions`

Tracks each execution of a scheduled task.

```sql
CREATE TABLE job_executions (
    id INTEGER PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,  -- 'RUNNING', 'COMPLETED', 'FAILED'
    
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    tweets_fetched INTEGER DEFAULT 0,
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_job_executions_job_id ON job_executions(job_id);
CREATE INDEX ix_job_executions_created_at ON job_executions(created_at);
```

**Purpose**: 
- Log every time a scheduled task runs
- Track success/failure status
- Store metrics (tweets fetched, errors)
- Enable execution history viewing

### 3. Updated Table: `summaries`

Extended to support both scheduled tasks and playground runs.

**New Columns**:
```sql
ALTER TABLE summaries ADD COLUMN execution_id INTEGER REFERENCES job_executions(id) ON DELETE SET NULL;
ALTER TABLE summaries ADD COLUMN is_playground BOOLEAN DEFAULT FALSE NOT NULL;
ALTER TABLE summaries ADD COLUMN x_username VARCHAR(255);
ALTER TABLE summaries ADD COLUMN topics JSON;
ALTER TABLE summaries ADD COLUMN hours_back INTEGER;
ALTER TABLE summaries ALTER COLUMN job_id DROP NOT NULL;  -- Make optional for playground runs

CREATE INDEX ix_summaries_execution_id ON summaries(execution_id);
CREATE INDEX ix_summaries_is_playground ON summaries(is_playground);
```

**Purpose**:
- `execution_id`: Link summary to specific job execution
- `is_playground`: Flag to distinguish playground runs from scheduled tasks
- `x_username`, `topics`, `hours_back`: Store playground run parameters
- `job_id` now optional: Playground runs don't have associated jobs

## Migration Instructions

### For Local Development (SQLite)

**Option 1: Fresh Database** (Recommended if you have no important data)

```bash
cd backend

# Backup current database (optional)
cp xtrack.db xtrack.db.backup

# Delete old database
rm xtrack.db

# Run the application - it will create the new schema automatically
python -m uvicorn app.main:app --reload
```

**Option 2: Use Alembic Migration**

```bash
cd backend
source venv/bin/activate

# Apply the migration
alembic upgrade head

# Check migration status
alembic current
```

### For Production (PostgreSQL on Railway)

**Important**: Always backup before migration!

```bash
cd backend
source venv/bin/activate

# Set DATABASE_URL to your Railway PostgreSQL
export DATABASE_URL="postgresql://user:password@host:port/database"

# Run migration
alembic upgrade head

# Verify
alembic current
```

**Via Railway CLI**:

Railway will automatically run migrations if you:
1. Push the code to GitHub
2. Railway redeploys
3. The application startup creates tables via `Base.metadata.create_all()`

OR manually connect and run:
```bash
railway run alembic upgrade head
```

## Data Model Relationships

```
User (1) ──────< (N) Job (Scheduled Task)
                       │
                       ├────< (N) JobExecution (Run History)
                       │              │
                       │              └────< (N) Summary (from scheduled run)
                       │
                       └────< (N) Summary (directly from job)

Summary (from playground run) - standalone, no job/execution links
```

## Usage Examples

### 1. Creating a Job Execution Record

```python
from app.models import JobExecution, ExecutionStatus
from app.database import SessionLocal

db = SessionLocal()

execution = JobExecution(
    job_id=1,
    status=ExecutionStatus.RUNNING
)
db.add(execution)
db.commit()
db.refresh(execution)

# Later, when complete:
execution.status = ExecutionStatus.COMPLETED
execution.completed_at = datetime.utcnow()
execution.tweets_fetched = 25
db.commit()
```

### 2. Creating a Scheduled Task Summary

```python
summary = Summary(
    job_id=1,
    execution_id=execution.id,
    is_playground=False,
    content="AI generated summary...",
    tweets_count=25,
    raw_data={"count": 25, "tweets": [...]}
)
db.add(summary)
db.commit()
```

### 3. Creating a Playground Run Summary

```python
summary = Summary(
    job_id=None,  # No associated job
    execution_id=None,  # No execution record
    is_playground=True,
    x_username="elonmusk",
    topics=["AI", "Tesla"],
    hours_back=24,
    content="AI generated summary...",
    tweets_count=15,
    raw_data={"count": 15, "tweets": [...]}
)
db.add(summary)
db.commit()
```

### 4. Querying Execution History

```python
# Get all executions for a job
executions = db.query(JobExecution).filter(
    JobExecution.job_id == job_id
).order_by(JobExecution.created_at.desc()).all()

# Get failed executions
failed = db.query(JobExecution).filter(
    JobExecution.status == ExecutionStatus.FAILED
).all()

# Get execution with its summary
execution = db.query(JobExecution).filter(
    JobExecution.id == execution_id
).first()
summaries = execution.summaries  # All summaries from this execution
```

### 5. Filtering Summaries

```python
# Get only playground runs
playground_summaries = db.query(Summary).filter(
    Summary.is_playground == True
).all()

# Get only scheduled task summaries
scheduled_summaries = db.query(Summary).filter(
    Summary.is_playground == False,
    Summary.job_id.isnot(None)
).all()

# Get summaries for a specific user's jobs
user_summaries = db.query(Summary).join(Job).filter(
    Job.user_id == user_id
).all()
```

## API Updates Needed

### 1. Update Monitoring Service

Modify `backend/app/services/monitoring_service.py`:
- Create `JobExecution` record when starting a job run
- Update execution status on completion/failure
- Link summaries to executions

### 2. Update Test Endpoint

Modify `backend/app/routers/monitoring.py` `/test` endpoint:
- Set `is_playground=True` for test summaries
- Store test parameters (x_username, topics, hours_back)
- Don't create job or execution records

### 3. Add Execution History Endpoint

```python
@router.get("/jobs/{job_id}/executions")
def get_job_executions(job_id: int, db: Session = Depends(get_db)):
    """Get execution history for a job"""
    executions = db.query(JobExecution).filter(
        JobExecution.job_id == job_id
    ).order_by(JobExecution.created_at.desc()).limit(50).all()
    return executions
```

### 4. Update Summary Endpoints

Modify to handle both playground and scheduled summaries:
- Filter by `is_playground` when appropriate
- Include execution information when available

## Rollback Instructions

If you need to rollback the migration:

```bash
cd backend
source venv/bin/activate

# Rollback one migration
alembic downgrade -1

# Or rollback to specific revision
alembic downgrade <revision_id>
```

**Warning**: Rollback will:
- Drop the `job_executions` table (losing all execution history)
- Remove playground-related columns from `summaries`
- Make `job_id` required again in summaries (may cause errors if playground runs exist)

## Testing the Migration

After migration, test:

1. **User Registration**: Verify new users have `status='UNVERIFIED'`
2. **Email Verification**: Check status changes to `ACTIVE` after verification
3. **Scheduled Task Run**: Ensure `JobExecution` records are created
4. **Playground Run**: Verify summaries with `is_playground=True` are created
5. **Execution History**: Query job executions via API
6. **Summary Queries**: Test filtering by playground vs scheduled

## Monitoring

After deployment, monitor:
- Database size (new table and columns will increase storage)
- Query performance (new indexes should help)
- Application logs for any migration errors
- API response times for summary queries

## Support

If you encounter issues:
1. Check alembic logs: `alembic history`
2. Verify current version: `alembic current`
3. Check database manually: Connect to DB and inspect schema
4. Review application logs for SQLAlchemy errors

