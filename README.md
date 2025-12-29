# XTrack - X Account Monitoring & AI Summarization

XTrack is a full-stack application that allows users to monitor specific X (Twitter) accounts and receive AI-generated summaries of their content based on topics of interest.

## ✨ Features

- **Account Monitoring**: Track multiple X accounts simultaneously
- **Flexible Scheduling**: Set monitoring frequency (hourly, 6 hours, 12 hours, daily)
- **Topic Emphasis**: AI focuses on your topics of interest in summaries
- **AI Summarization**: Get intelligent summaries using Google Gemini
- **Email Notifications**: Receive summaries via email (Gmail OAuth)
- **Automatic Scheduling**: Jobs run 24/7 using APScheduler
- **Database Storage**: PostgreSQL for persistent storage
- **Modern UI**: Clean, minimalist white design with black buttons

## 🛠️ Tech Stack

- **Frontend**: React + Vite + Lucide Icons
- **Backend**: Python 3.13 + FastAPI + SQLAlchemy
- **Database**: PostgreSQL (SQLite for local development)
- **Scheduling**: APScheduler for automatic job execution
- **Twitter API**: twitterapi.io
- **LLM**: Google Gemini (gemini-2.5-flash)
- **Email**: Gmail API with OAuth 2.0
- **Deployment**: Railway (Backend + DB) + Vercel (Frontend)

## Project Structure

```
xtrack/
├── backend/
│   ├── app/
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic (Twitter, LLM, Monitoring)
│   │   ├── models.py       # Database models
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── database.py    # Database configuration
│   │   ├── scheduler.py    # Job scheduling
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:
```bash
cp .env.example .env
```

5. Edit `.env` and add your API keys (see `.env.example` for detailed instructions):
   - **Twitter API**: Get from https://twitterapi.io/dashboard
   - **Gemini API**: Get from https://makersuite.google.com/app/apikey
   - **Gmail API (optional)**: See `backend/GMAIL_SETUP.md` for detailed setup

```env
# Required
TWITTER_API_KEY=your_twitter_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Optional - for email summaries (Gmail API with OAuth)
FROM_EMAIL=your_email@gmail.com
# See backend/GMAIL_SETUP.md for complete Gmail API setup
```

6. Run the backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🔌 API Endpoints

### Health
- `GET /` - API root message
- `GET /health` - Health check

### Jobs
- `POST /api/jobs/` - Create a monitoring job
- `GET /api/jobs/` - Get all jobs
- `GET /api/jobs/{job_id}` - Get a specific job
- `PATCH /api/jobs/{job_id}` - Update a job (frequency, topics, email, is_active)
- `DELETE /api/jobs/{job_id}` - Delete a job
- `GET /api/jobs/{job_id}/summaries` - Get summaries for a job

### Monitoring
- `POST /api/monitoring/test` - Test monitoring with immediate execution
- `POST /api/monitoring/jobs/{job_id}/run` - Manually trigger a job
- `POST /api/monitoring/jobs/{job_id}/summaries/send-email` - Send existing summary via email

See full API docs at: `http://localhost:8000/docs` (when running locally)

## 💡 Usage

### Quick Test (No Job Creation)
1. Click **"Show Test"** button
2. Enter X username (e.g., `elonmusk`)
3. Set time range (hours back)
4. Optionally add topics and email
5. Click **"Run Test"** to see immediate results

### Create Monitoring Jobs
1. Click **"Add Job"** button
2. Enter the X username (without @)
3. Select monitoring frequency (hourly, 6h, 12h, daily)
4. Add topics of interest (comma-separated, optional)
5. Add email for automatic notifications (optional)
6. Jobs run automatically based on schedule

### View & Manage
- **View Summaries**: Click "View Summaries" on any job
- **Run Manually**: Click ▶ play button for immediate execution
- **Send Email**: Click 📧 icon to resend a summary
- **Pause/Resume**: Toggle job active status
- **Delete**: Remove jobs you no longer need

## Environment Variables

See `backend/.env.example` for detailed setup instructions with links.

### Required
- `TWITTER_API_KEY`: Your twitterapi.io API key ([Get it here](https://twitterapi.io/dashboard))
- `GEMINI_API_KEY`: Your Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))
  - Or `OPENAI_API_KEY`: Your OpenAI API key ([Get it here](https://platform.openai.com/api-keys))

### Optional - Gmail API Configuration (for email summaries)
- `FROM_EMAIL`: Sender email address
- `GMAIL_CREDENTIALS_FILE`: Path to OAuth credentials (default: credentials.json)
- `GMAIL_TOKEN_FILE`: Path to token file (default: token.pickle)

**Note**: This app uses Gmail API with OAuth 2.0 instead of SMTP for better security.
See `backend/GMAIL_SETUP.md` for detailed setup instructions.

### Server Configuration
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `TWITTER_API_BASE_URL`: Twitter API base URL (default: `https://api.twitterapi.io`)

## 📦 Database

The application uses **PostgreSQL** in production and **SQLite** for local development:

- **Users**: Store user information
- **Jobs**: Monitor job configurations (username, frequency, topics, email)
- **Summaries**: AI-generated summaries with timestamps and raw data

All data persists across server restarts.

## 🚀 Deployment

### Quick Deploy (15 minutes)

See [QUICK_DEPLOY.md](QUICK_DEPLOY.md) for a streamlined deployment guide.

### Full Deployment Guide

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed step-by-step instructions.

### Deployment Options

1. **Railway + Vercel** (Recommended)
   - Backend + Database on Railway ($5/month)
   - Frontend on Vercel (Free)
   - **Total: $5/month**

2. **AWS**
   - Backend: EC2/ECS/Lambda
   - Database: RDS PostgreSQL
   - Frontend: S3 + CloudFront
   - **Total: ~$20-50/month**

3. **Docker + DigitalOcean**
   - Single droplet with Docker Compose
   - **Total: $6-12/month**

**Recommended for beginners**: Railway + Vercel (easiest setup, great free tier)

## 📝 Notes

- **Rate Limiting**: Twitter API free tier allows 1 request every 5 seconds (auto-handled)
- **Job Scheduling**: Jobs run automatically 24/7 via APScheduler
- **Email**: Uses Gmail API with OAuth 2.0 (see `backend/GMAIL_SETUP.md`)
- **Topics**: Topics are emphasized in AI summaries, not used for filtering
- **Test Function**: Available in UI for immediate testing without creating jobs
- **Deployment**: Frontend and backend can scale independently

## License

MIT

