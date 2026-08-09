"""Meal diary endpoints - no business logic here, delegates to the controller."""

from flasgger import swag_from
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.controllers import meal_log_controller

meal_logs_bp = Blueprint("meal_logs", __name__, url_prefix="/api/v1/meal-logs")


@meal_logs_bp.post("")
@jwt_required()
@swag_from("../docs/meal_logs/log_meal.yml")
def log_meal():
    body, status_code = meal_log_controller.handle_log_meal(
        get_jwt_identity(), request.get_json(silent=True)
    )
    return jsonify(body), status_code


@meal_logs_bp.get("")
@jwt_required()
@swag_from("../docs/meal_logs/get_history.yml")
def get_history():
    body, status_code = meal_log_controller.handle_get_history(get_jwt_identity())
    return jsonify(body), status_code
