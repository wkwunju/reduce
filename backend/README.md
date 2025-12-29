# Backend Setup

## Quick Start

1. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create `.env` file:**
Create a `.env` file in the `backend` directory with the following content:

```env
# Twitter API (twitterapi.io)
TWITTER_API_KEY=your_twitter_api_key_here
# Get your API key from: https://twitterapi.io/dashboard
TWITTER_API_BASE_URL=https://api.twitterapi.io

# LLM Configuration
GEMINI_API_KEY=your_gemini_api_key_here
# Optional: GEMINI_MODEL=gemini-2.5-flash (default) or gemini-1.5-flash, gemini-1.5-pro
# Alternative: OPENAI_API_KEY=your_openai_api_key_here

# Email Configuration (SendGrid - recommended)
# Get your API key from: https://app.sendgrid.com/settings/api_keys
SENDGRID_API_KEY=SG.your_sendgrid_api_key_here
FROM_EMAIL=kai@ai-productivity.tools

# Server
HOST=0.0.0.0
PORT=8000
```

4. **Setup Email Service (optional, for email summaries):**
   - **SendGrid (Recommended):**
     1. Sign up at https://signup.sendgrid.com/
     2. Create API Key: Settings → API Keys → Create API Key
     3. Verify sender email: Settings → Sender Authentication → Single Sender Verification
     4. Add to `.env`: `SENDGRID_API_KEY` and `FROM_EMAIL`
   - Free tier: 100 emails/day permanently

5. **Run the server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Email Setup (SendGrid)

For sending email summaries, this application uses **SendGrid API** for reliable delivery.

### Quick Setup:
1. **Sign up**: https://signup.sendgrid.com/ (free tier: 100 emails/day)
2. **Create API Key**: Settings → API Keys → Create API Key
   - Choose "Restricted Access" → Enable "Mail Send" (Full Access)
   - Copy the API key (starts with `SG.`)
3. **Verify Sender**: Settings → Sender Authentication → Single Sender Verification
   - Add your email (e.g., `kai@ai-productivity.tools`)
   - Check email and click verification link
4. **Configure**: Add to `.env`:
   ```
   SENDGRID_API_KEY=SG.your_api_key_here
   FROM_EMAIL=kai@ai-productivity.tools
   ```

## Notes

- **Python Version**: Requires Python 3.10+ (tested with Python 3.13)
- **Database**: Uses PostgreSQL in production (Railway), SQLite for local development
- **Email**: Optional feature using SendGrid API. Free tier: 100 emails/day.
- Make sure to get your API keys from:
  - Twitter API: https://twitterapi.io/dashboard
  - Gemini API: https://makersuite.google.com/app/apikey
  - SendGrid API: https://app.sendgrid.com/settings/api_keys

