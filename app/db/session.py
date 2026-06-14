import os
import socket
from urllib.parse import urlparse, urlunparse

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


def _force_ipv4_url(url: str) -> str:
    """Resolve Supabase hostname to IPv4 address to avoid Vercel IPv6 issues."""
    if "supabase.co" not in url:
        return url

    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    try:
        # Try to get IPv4 address only
        addrs = socket.getaddrinfo(hostname, parsed.port or 5432, socket.AF_INET)
        if addrs:
            ipv4 = addrs[0][4][0]
            # Replace hostname with IPv4 address
            new_netloc = parsed.netloc.replace(hostname, ipv4)
            url = urlunparse(parsed._replace(netloc=new_netloc))
    except OSError:
        pass  # Fall back to hostname if resolution fails

    return url


connect_args = {}
if settings.database_url and "supabase.co" in settings.database_url:
    connect_args["prepare_threshold"] = None

# Use modified URL with IPv4 address if needed
db_url = _force_ipv4_url(settings.database_url) if settings.database_url else settings.database_url

engine = create_engine(db_url, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()