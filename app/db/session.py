import logging
import socket

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)


def _db_is_reachable() -> bool:
    """Check if the database host is reachable (quick DNS check)."""
    url = settings.database_url
    if not url:
        return True

    try:
        hostname = url.split("@")[1].split(":")[0] if "@" in url else ""
        if not hostname:
            return True
        # Check if we can resolve to an IPv4 address
        addrs = socket.getaddrinfo(hostname, 5432, socket.AF_INET, socket.SOCK_STREAM)
        return len(addrs) > 0
    except (OSError, Exception) as exc:
        logger.warning("Database host unreachable: %s", exc)
        return False


_db_available = _db_is_reachable()

if _db_available:
    connect_args = {}
    if settings.database_url and ("neon.tech" in settings.database_url or "supabase.co" in settings.database_url):
        connect_args["prepare_threshold"] = None
        connect_args["connect_timeout"] = 3

    engine = create_engine(
        settings.database_url,
        pool_pre_ping=False,
        connect_args=connect_args,
        pool_timeout=3,
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
else:
    engine = None  # type: ignore
    SessionLocal = None


class Base(DeclarativeBase):
    pass


def get_db():
    """Yields a DB session, or None if the database is unreachable."""
    if not _db_available or SessionLocal is None:
        yield None
        return

    try:
        db = SessionLocal()
        yield db
        db.close()
    except Exception as exc:
        logger.warning("Database unavailable, operating without persistence: %s", exc)
        yield None