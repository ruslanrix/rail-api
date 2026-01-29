from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Notification

import logging
import time


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


logger = logging.getLogger(__name__)


def deliver_notification(message: str, request_id: str | None) -> None:
    """
    Background delivery simulation.

    Must never raise (background task should not crash request lifecycle/tests).
    """
    try:
        # Simulate some work.
        time.sleep(0.01)
        logger.info("delivered notification request_id=%s message=%r", request_id or "-", message)
    except Exception:
        logger.exception("background delivery failed request_id=%s", request_id or "-")
