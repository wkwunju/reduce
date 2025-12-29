# XTrack Setup Guide

This guide will walk you through setting up XTrack from scratch.

## Prerequisites

- Python 3.10+ (tested with Python 3.13)
- Node.js 16+ and npm
- Git

## Backend Setup

### Step 1: Clone and Navigate

```bash
cd /path/to/xtrack
cd backend
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

1. **Copy the example file:**
```bash
cp .env.example .env
```

2. **Edit the `.env` file and configure:**

#### Required Configuration

##### Twitter API (twitterapi.io)
1. Sign up at [https://twitterapi.io](https://twitterapi.io)
2. Go to [Dashboard](https://twitterapi.io/dashboard)
3. Copy your API key
4. Add to `.env`:
```env
TWITTER_API_KEY=your_actual_api_key_here
TWITTER_API_BASE_URL=https://api.twitterapi.io
```

##### LLM Configuration (Choose One)

**Option 1: Google Gemini (Recommended)**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key
4. Add to `.env`:
```env
GEMINI_API_KEY=your_actual_gemini_key_here
GEMINI_MODEL=gemini-2.5-flash
```

**Option 2: OpenAI ChatGPT (Alternative)**
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Copy the key
4. Add to `.env`:
```env
OPENAI_API_KEY=your_actual_openai_key_here
```

#### Optional: Email Configuration

Email sending is **optional**. If configured, summaries will be automatically sent via email when jobs run.

##### For Gmail:

1. **Enable 2-Step Verification:**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable "2-Step Verification"

2. **Generate App Password:**
   - Go to [App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and your device
   - Click "Generate"
   - Copy the 16-character password (no spaces)

3. **Add to `.env`:**
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password_here
FROM_EMAIL=your_email@gmail.com
```

**Important:** Use the App Password, NOT your regular Gmail password!

##### For Outlook/Hotmail:

```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your_email@outlook.com
SMTP_PASSWORD=your_outlook_password
FROM_EMAIL=your_email@outlook.com
```

##### For Yahoo Mail:

1. Enable "Allow apps that use less secure sign in" OR generate an App Password
2. Add to `.env`:
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=your_email@yahoo.com
SMTP_PASSWORD=your_yahoo_app_password
FROM_EMAIL=your_email@yahoo.com
```

##### For Other SMTP Servers:

```env
SMTP_SERVER=smtp.your-provider.com
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
FROM_EMAIL=noreply@yourdomain.com
```

### Step 5: Run the Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: **http://localhost:8000**

API Documentation:
- Swagger UI: **http://localhost:8000/docs**
- ReDoc: **http://localhost:8000/redoc**

---

## Frontend Setup

### Step 1: Navigate to Frontend

```bash
cd ../frontend  # From backend directory
# OR
cd /path/to/xtrack/frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Run the Development Server

```bash
npm run dev
```

The frontend will be available at: **http://localhost:5173**

---

## Quick Test

1. **Open the frontend** in your browser: http://localhost:5173
2. **Create a test job:**
   - Click "Add Job"
   - Enter an X username (e.g., `elonmusk`)
   - Select a frequency
   - Add topics (optional)
   - Add email address (optional)
   - Click "Create Job"
3. **Run the test:**
   - Go to "Quick Test" section
   - Enter a username and time range
   - Click "Run Test"
   - View the AI summary

---

## Troubleshooting

### Backend Issues

**Error: `TWITTER_API_KEY not found`**
- Make sure you've created the `.env` file from `.env.example`
- Check that `TWITTER_API_KEY` is set in `.env`
- Restart the backend server

**Error: `No LLM API key found`**
- Make sure either `GEMINI_API_KEY` or `OPENAI_API_KEY` is set in `.env`
- Restart the backend server

**Error: `Rate limit exceeded` (429)**
- The free tier of twitterapi.io allows 1 request per 5 seconds
- The app automatically handles this with delays
- Wait a few seconds and try again

**Email not working:**
- Email is optional - the app works without it
- For Gmail, make sure you're using an App Password, not your regular password
- Check that 2-Step Verification is enabled for Gmail
- Verify SMTP credentials are correct
- Check logs for email error messages

### Frontend Issues

**Cannot connect to backend:**
- Make sure the backend is running on http://localhost:8000
- Check CORS settings in `backend/app/main.py`

**Port already in use:**
- Frontend: Change port in `vite.config.js` or kill the process using port 5173
- Backend: Change port in `.env` or kill the process using port 8000

---

## Environment Variable Summary

### Backend `.env` File

```env
# Required
TWITTER_API_KEY=your_key_here
TWITTER_API_BASE_URL=https://api.twitterapi.io
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash

# Optional - Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
FROM_EMAIL=your_email@gmail.com

# Server (defaults shown)
HOST=0.0.0.0
PORT=8000
```

---

## Next Steps

- See `README.md` for feature details and usage instructions
- See `backend/README.md` for backend API documentation
- See `frontend/README.md` for frontend development details

---

## Support

If you encounter issues:
1. Check the console logs (backend terminal and browser console)
2. Verify all API keys are correct
3. Make sure you've restarted the server after changing `.env`
4. Check the troubleshooting section above

---

## Notes

- **Storage:** Currently uses in-memory storage. Data will be lost on server restart. Database support coming later.
- **Email:** Optional feature. App works without email configuration.
- **Rate Limits:** Free tier of twitterapi.io: 1 request per 5 seconds
- **Security:** Never commit your `.env` file to git (it's in `.gitignore`)

