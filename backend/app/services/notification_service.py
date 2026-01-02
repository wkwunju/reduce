from datetime import datetime, timedelta
import secrets
from typing import Optional, Dict, List
from sqlalchemy.orm import Session

from app.models import NotificationTarget, NotificationBindToken, NotificationChannel
from app.services.telegram_service import TelegramService


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.telegram_service = TelegramService()

    def create_bind_token(self, user_id: int, channel: NotificationChannel, ttl_minutes: int = 10) -> Dict:
        token = secrets.token_urlsafe(16)
        expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)
        record = NotificationBindToken(
            user_id=user_id,
            channel=channel,
            token=token,
            expires_at=expires_at,
            used=False
        )
        self.db.add(record)
        self.db.commit()
        return {"token": token, "expires_at": expires_at.isoformat()}

    def bind_target_from_token(
        self,
        token: str,
        destination: str,
        metadata: Optional[dict] = None
    ) -> Optional[NotificationTarget]:
        record = self.db.query(NotificationBindToken).filter(
            NotificationBindToken.token == token,
            NotificationBindToken.used.is_(False),
            NotificationBindToken.expires_at > datetime.utcnow()
        ).first()
        if not record:
            return None

        existing = self.db.query(NotificationTarget).filter(
            NotificationTarget.user_id == record.user_id,
            NotificationTarget.channel == record.channel,
            NotificationTarget.destination == destination
        ).first()

        if existing:
            existing.meta = metadata or existing.meta
            target = existing
        else:
            has_default = self.db.query(NotificationTarget).filter(
                NotificationTarget.user_id == record.user_id,
                NotificationTarget.channel == record.channel,
                NotificationTarget.is_default.is_(True)
            ).first()
            target = NotificationTarget(
                user_id=record.user_id,
                channel=record.channel,
                destination=destination,
                meta=metadata,
                is_default=has_default is None
            )
            self.db.add(target)

        record.used = True
        self.db.commit()
        return target

    def list_targets(self, user_id: int):
        return self.db.query(NotificationTarget).filter(
            NotificationTarget.user_id == user_id
        ).order_by(NotificationTarget.created_at.desc()).all()

    def set_default_target(self, user_id: int, target_id: int) -> Optional[NotificationTarget]:
        target = self.db.query(NotificationTarget).filter(
            NotificationTarget.id == target_id,
            NotificationTarget.user_id == user_id
        ).first()
        if not target:
            return None

        self.db.query(NotificationTarget).filter(
            NotificationTarget.user_id == user_id,
            NotificationTarget.channel == target.channel,
            NotificationTarget.is_default.is_(True)
        ).update({"is_default": False})
        target.is_default = True
        self.db.commit()
        return target

    def get_default_target(self, user_id: int, channel: NotificationChannel) -> Optional[NotificationTarget]:
        return self.db.query(NotificationTarget).filter(
            NotificationTarget.user_id == user_id,
            NotificationTarget.channel == channel,
            NotificationTarget.is_default.is_(True)
        ).first()

    def send_summary(
        self,
        user_id: int,
        x_username: str,
        summary: str,
        tweets_count: int,
        topics: Optional[list],
        time_range: Optional[str],
        target_id: Optional[int] = None,
        target_ids: Optional[List[int]] = None,
        headline: Optional[str] = None
    ) -> bool:
        message = self.telegram_service.build_summary_message(
            x_username=x_username,
            summary=summary,
            tweets_count=tweets_count,
            topics=topics,
            time_range=time_range,
            headline=headline
        )
        effective_target_ids = target_ids or ([target_id] if target_id else [])
        if effective_target_ids:
            targets = self.db.query(NotificationTarget).filter(
                NotificationTarget.id.in_(effective_target_ids),
                NotificationTarget.user_id == user_id,
                NotificationTarget.channel == NotificationChannel.TELEGRAM
            ).all()
            if not targets:
                return False
            sent_any = False
            for target in targets:
                sent_any = self.telegram_service.send_message(target.destination, message) or sent_any
            return sent_any

        target = self.get_default_target(user_id, NotificationChannel.TELEGRAM)
        if not target:
            return False
        return self.telegram_service.send_message(target.destination, message)
