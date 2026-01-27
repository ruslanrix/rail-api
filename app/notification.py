from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Notification


def create_notification(db: Session, *, message: str) -> Notification:
    obj = Notification(message=message)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_notification(db: Session, notification_id: int) -> Notification | None:
    return db.get(Notification, notification_id)


def list_notifications(db: Session, *, limit: int = 50, offset: int = 0) -> list[Notification]:
    stmt = select(Notification).order_by(Notification.id.desc()).limit(limit).offset(offset)
    return list(db.execute(stmt).scalars().all())
