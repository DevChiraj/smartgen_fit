"""Request/response orchestration for the smart notifications endpoint."""

from app.repositories import user_repository
from app.services import notification_service


def handle_get_notifications(user_id: str):
    user = user_repository.get_by_id(int(user_id))
    notifications = notification_service.get_notifications(user)
    return {"notifications": notifications}, 200
