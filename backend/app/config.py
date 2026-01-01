import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: Optional[str] = None
    
    # Twitter API
    twitter_api_key: str
    
    # Gemini API
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash-exp"
    
    # Email (SendGrid)
    sendgrid_api_key: str
    from_email: str
    
    # Authentication
    session_secret: str

    # Telegram
    telegram_bot_token: Optional[str] = None
    telegram_webhook_dev: Optional[str] = None
    telegram_webhook_railway: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        # Map environment variables to lowercase field names
        fields = {
            'database_url': {'env': 'DATABASE_URL'},
            'twitter_api_key': {'env': 'TWITTER_API_KEY'},
            'gemini_api_key': {'env': 'GEMINI_API_KEY'},
            'gemini_model': {'env': 'GEMINI_MODEL'},
            'sendgrid_api_key': {'env': 'SENDGRID_API_KEY'},
            'from_email': {'env': 'FROM_EMAIL'},
            'session_secret': {'env': 'SESSION_SECRET'},
            'telegram_bot_token': {'env': 'TELEGRAM_BOT_TOKEN'},
            'telegram_webhook_dev': {'env': 'TELEGRAM_WEBHOOK_DEV'},
            'telegram_webhook_railway': {'env': 'TELEGRAM_WEBHOOK_RAILWAY'},
        }

settings = Settings()
