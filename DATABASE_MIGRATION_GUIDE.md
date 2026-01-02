# Database Migration Guide

This project uses Alembic for schema migrations.

## How to Migrate

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

Check current version:
```bash
alembic current
```

## Current Schema Highlights

### Jobs
- `language` (default `en`)
- `status` enum: `active` / `deleted` (soft delete)
- `notification_target_id` (legacy single target)
- `job_notification_targets` join table for multi-target Telegram

### Summaries
- `input_tokens`, `output_tokens`
- `execution_id` for job run linkage
- `is_playground` + `x_username` + `topics` + `hours_back` for playground

### Job Executions
Tracks each scheduled run:
- status (`RUNNING`, `COMPLETED`, `FAILED`)
- timestamps and metrics

### Notifications
- `notification_targets`
- `notification_bind_tokens`

## Notes
- Deleting a job is a soft delete (`status=deleted`), executions and summaries are preserved.
- Playground runs are saved as summaries with `is_playground=true`.
