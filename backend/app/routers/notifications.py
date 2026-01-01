from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import NotificationChannel, User
from app.services.notification_service import NotificationService
from app.services.telegram_service import TelegramService

router = APIRouter()


class BindTokenResponse(BaseModel):
    token: str
    expires_at: str


@router.post("/telegram/bind-token", response_model=BindTokenResponse)
def create_telegram_bind_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    token_info = service.create_bind_token(current_user.id, NotificationChannel.TELEGRAM)
    return token_info


@router.get("/targets")
def list_notification_targets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    targets = service.list_targets(current_user.id)
    return [
        {
            "id": t.id,
            "channel": t.channel.value if t.channel else None,
            "destination": t.destination,
            "metadata": t.meta,
            "is_default": t.is_default,
            "created_at": t.created_at.isoformat() if t.created_at else None
        }
        for t in targets
    ]


@router.patch("/targets/{target_id}/default")
def set_default_notification_target(
    target_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    target = service.set_default_target(current_user.id, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Notification target not found")
    return {"status": "ok"}


@router.post("/telegram/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    message = payload.get("message") or payload.get("edited_message") or payload.get("channel_post")
    if not message:
        return {"ok": True}

    text = message.get("text") or ""
    parts = text.strip().split()
    if not parts or parts[0] not in ["/start", "/bind"]:
        return {"ok": True}

    if len(parts) < 2:
        return {"ok": True}

    token = parts[1].strip()
    chat = message.get("chat", {})
    chat_id = str(chat.get("id"))
    chat_title = chat.get("title") or " ".join(
        p for p in [chat.get("first_name"), chat.get("last_name")] if p
    )
    chat_title = chat_title or chat.get("username") or chat_id
    chat_type = chat.get("type")

    service = NotificationService(db)
    target = service.bind_target_from_token(
        token=token,
        destination=chat_id,
        metadata={"title": chat_title, "type": chat_type}
    )

    telegram = TelegramService()
    if target:
        telegram.send_message(chat_id, "XTrack: Telegram linked successfully.")
    else:
        telegram.send_message(chat_id, "XTrack: Invalid or expired token.")

    return {"ok": True}
