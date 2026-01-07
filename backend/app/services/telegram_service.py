import os
from typing import Optional
import requests


class TelegramService:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.api_base = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None

    def send_message(self, chat_id: str, text: str) -> bool:
        if not self.api_base:
            print("[TELEGRAM] ⚠️  TELEGRAM_BOT_TOKEN not set, skipping send")
            return False

        try:
            response = requests.post(
                f"{self.api_base}/sendMessage",
                json={"chat_id": chat_id, "text": text},
                timeout=10
            )
            if response.status_code == 200:
                return True
            print(f"[TELEGRAM] ⚠️  sendMessage failed: {response.status_code} {response.text}")
            return False
        except Exception as e:
            print(f"[TELEGRAM] ❌ Error sending message: {e}")
            return False

    def build_summary_message(
        self,
        x_username: str,
        summary: str,
        tweets_count: int,
        topics: Optional[list],
        time_range: Optional[str],
        headline: Optional[str] = None
    ) -> str:
        topics_line = f"Topics: {', '.join(topics)}" if topics else "Topics: (none)"
        time_line = f"Time range: {time_range}" if time_range else "Time range: (n/a)"
        account_line = self._format_account_line(x_username)
        headline_line = f"XTrack Flash: {headline}\n" if headline else ""
        return (
            f"{headline_line}"
            f"{summary}\n\n"
            "Input Details\n"
            f"{account_line}\n"
            f"{time_line}\n"
            f"Tweets analyzed: {tweets_count}\n"
            f"{topics_line}\n\n"
            "More: https://www.ai-productivity.tools/"
        )

    def _format_account_line(self, x_username: Optional[str]) -> str:
        if not x_username:
            return "Account: (unknown)"
        names = [name.strip().lstrip("@") for name in str(x_username).split(",") if name.strip()]
        if not names:
            return "Account: (unknown)"
        if len(names) == 1:
            return f"Account: @{names[0]}"
        return f"Accounts: @{', @'.join(names)}"
