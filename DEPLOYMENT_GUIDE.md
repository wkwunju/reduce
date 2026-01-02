# Deployment Guide

Deploy XTrack to Railway (backend + PostgreSQL) and Vercel (frontend).

## Railway (Backend + DB)
1. Create project from GitHub repo
2. Add PostgreSQL database (Railway sets `DATABASE_URL`)
3. Set variables:
```
TWITTER_API_KEY=...
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash
OPENAI_API_KEY=...      # optional
SENDGRID_API_KEY=...    # optional
FROM_EMAIL=...
SESSION_SECRET=...
FRONTEND_ORIGINS=https://your-frontend-domain,https://www.your-frontend-domain
```
4. Deploy
5. Run migrations:
```bash
alembic upgrade head
```
6. Generate Railway domain and copy backend URL

## Vercel (Frontend)
Set `VITE_API_URL` to:
```
https://your-backend-domain.up.railway.app/api
```
Deploy to production.

## Telegram Webhook (Production)
Set webhook to Railway:
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -d "url=https://your-backend-domain.up.railway.app/api/notifications/telegram/webhook"
```
Verify:
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

## Verification
- Backend: `GET /health`
- Auth: login/register works
- Jobs: create/run job
- Notifications: email + Telegram

## Troubleshooting
- CORS: ensure frontend domain is in `FRONTEND_ORIGINS` and redeploy
- DB errors: run `alembic upgrade head`
