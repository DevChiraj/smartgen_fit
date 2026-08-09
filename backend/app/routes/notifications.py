"""Smart notifications endpoint - no business logic here, delegates to the controller."""

from flasgger import swag_from
from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.controllers import notification_controller

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/v1/notifications")


@notifications_bp.get("")
@jwt_required()
@swag_from("../docs/notifications/get_notifications.yml")
def get_notifications():
    body, status_code = notification_controller.handle_get_notifications(get_jwt_identity())
    return jsonify(body), status_code
