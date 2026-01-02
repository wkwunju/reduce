# Auth Deployment Guide

## Required env vars (Railway)
```
SESSION_SECRET=<openssl rand -hex 32>
```

## Deploy
1. Push to GitHub
2. Railway redeploys backend
3. Run migrations:
```bash
alembic upgrade head
```

## Verify
- `POST /api/auth/login`
- `GET /api/auth/me` (returns 401 when not logged in)

## Notes
- UI is English-only per `backend/.rules.md`.
