"""Request/response orchestration for health endpoints."""

from app.services import health_service


def handle_api_health():
    return health_service.get_api_health(), 200


def handle_db_health():
    result = health_service.get_db_health()
    status_code = 200 if result["status"] == "ok" else 503
    return result, status_code
