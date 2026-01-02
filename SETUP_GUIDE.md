# XTrack Setup Guide

## Prerequisites
- Python 3.13+
- Node.js 18+ and npm
- Git

## Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set required env vars in `backend/.env`:
```env
TWITTER_API_KEY=your_twitter_api_key
GEMINI_API_KEY=your_gemini_api_key
# Optional
GEMINI_MODEL=gemini-2.5-flash
OPENAI_API_KEY=your_openai_api_key
```

Email (optional):
- SendGrid: see `SENDGRID_SETUP.md`
- Gmail API: see `backend/GMAIL_SETUP.md`

Run backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

Optional local API override (`frontend/.env.local`):
```env
VITE_API_URL=http://localhost:8000/api
```

## Health Check
```bash
curl http://localhost:8000/health
```
