"""Business logic for health checks."""

from sqlalchemy import text

from app.extensions import db


def get_api_health() -> dict:
    return {"status": "ok", "service": "smartgen-fit-api"}


def get_db_health() -> dict:
    try:
        db.session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as exc:  # noqa: BLE001 - surfaced to the client as a health signal
        return {"status": "error", "database": "unreachable", "detail": str(exc)}
