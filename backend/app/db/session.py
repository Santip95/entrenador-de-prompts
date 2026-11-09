from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.core.config import Settings, get_settings


def build_engine(settings: Settings | None = None) -> Engine:
    resolved = settings or get_settings()
    resolved.validate_runtime()
    return create_engine(
        resolved.resolved_database_url(),
        pool_pre_ping=True,
        future=True,
        hide_parameters=True,
    )
