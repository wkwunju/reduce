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

# Gmail API Configuration (optional - for sending summaries)
# See GMAIL_SETUP.md for detailed setup instructions
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.pickle
FROM_EMAIL=your_email@gmail.com

# Server
HOST=0.0.0.0
PORT=8000
```

4. **Setup Gmail API (optional, for email summaries):**
   - See **[GMAIL_SETUP.md](./GMAIL_SETUP.md)** for detailed instructions
   - Quick steps:
     1. Enable Gmail API in Google Cloud Console
     2. Download OAuth credentials as `credentials.json`
     3. Place in backend directory
     4. First run will open browser for authorization

5. **Run the server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Gmail API Setup

For sending email summaries, this application uses **Gmail API with OAuth 2.0** (more secure than SMTP).

See **[GMAIL_SETUP.md](./GMAIL_SETUP.md)** for complete setup instructions.

Quick overview:
1. Create a project in Google Cloud Console
2. Enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download credentials.json
5. First run will open browser for authorization

## Notes

- **Python Version**: Requires Python 3.10+ (tested with Python 3.13)
- **Storage**: Currently using in-memory storage. Jobs and summaries are stored in memory and will be lost on server restart. Database support will be added in a later stage.
- **Email**: Optional feature using Gmail API with OAuth 2.0. See GMAIL_SETUP.md for setup.
- Make sure to get your API keys from:
  - Twitter API: https://twitterapi.io (get your key from https://twitterapi.io/dashboard)
  - Gemini API: https://makersuite.google.com/app/apikey
  - OpenAI API: https://platform.openai.com/api-keys
  - Gmail API: See GMAIL_SETUP.md

