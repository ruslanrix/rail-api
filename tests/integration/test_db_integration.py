from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.notification import create_notification, get_notification
import pytest

pytestmark = pytest.mark.contract


def test_db_integration_create_and_get_notification():
    db: Session = SessionLocal()
    try:
        obj = create_notification(db, message="hello-db")
        fetched = get_notification(db, obj.id)
        assert fetched is not None
        assert fetched.id == obj.id
        assert fetched.message == "hello-db"
    finally:
        db.close()
