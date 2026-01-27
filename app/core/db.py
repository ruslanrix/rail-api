from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import get_settings


def _make_engine() -> Engine:
    s = get_settings()
    url = s.database_url

    connect_args: dict[str, object] = {}
    # SQLite needs this flag for multithreaded testclient usage.
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(
        url,
        echo=s.db_echo,
        future=True,
        connect_args=connect_args,
    )


engine: Engine = _make_engine()

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Minimal initializer (Module M).
    For now we create tables automatically.
    Later you can swap to Alembic migrations without changing callers.
    """
    from app.models import Base  # local import to avoid import cycles

    Base.metadata.create_all(bind=engine)
