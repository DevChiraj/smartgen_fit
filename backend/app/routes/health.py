"""Health check endpoints — no business logic here, delegates to the controller."""

from flask import Blueprint, jsonify

from app.controllers import health_controller

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.get("/health")
def api_health():
    body, status_code = health_controller.handle_api_health()
    return jsonify(body), status_code


@health_bp.get("/health/db")
def db_health():
    body, status_code = health_controller.handle_db_health()
    return jsonify(body), status_code
