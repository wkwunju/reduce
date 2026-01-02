# Quick Deploy

Deploy in ~15 minutes: Railway (backend + DB) + Vercel (frontend).

## 1) Push to GitHub
```bash
cd /Users/wenkai/ai-project/xtrack
git add .
git commit -m "Deploy" || true
git push origin main
```

## 2) Railway (Backend + DB)
1. Create Railway project from GitHub repo
2. Add PostgreSQL database (Railway sets `DATABASE_URL`)
3. Set env vars (Variables tab):
```
TWITTER_API_KEY=...
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash
FROM_EMAIL=...
SENDGRID_API_KEY=...   # optional
SESSION_SECRET=...     # auth required
FRONTEND_ORIGINS=https://your-frontend-domain
```
4. Deploy, then run migrations:
```bash
alembic upgrade head
```
5. Copy backend URL (e.g. `https://your-app.up.railway.app`)

## 3) Vercel (Frontend)
Set `VITE_API_URL` to `https://your-app.up.railway.app/api` and deploy.

## 4) Verify
- Backend: `GET /health`
- Frontend: login + create job
