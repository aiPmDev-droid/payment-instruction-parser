import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)


# If connecting to Supabase, configure for the connection pooler
connect_args = {}
if settings.database_url and "supabase.co" in settings.database_url:
    connect_args["prepare_threshold"] = None
    connect_args["connect_timeout"] = 3

# Short timeout + no pre-ping to avoid hanging on unreachable DB
engine = create_engine(
    settings.database_url,
    pool_pre_ping=False,
    connect_args=connect_args,
    pool_timeout=3,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    try:
        db = SessionLocal()
        yield db
        db.close()
    except Exception as exc:
        logger.warning("Failed to create DB session: %s", exc)
        yield None