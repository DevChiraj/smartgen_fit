"""Workout tracker endpoints - no business logic here, delegates to the controller."""

from flasgger import swag_from
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.controllers import workout_log_controller

workout_logs_bp = Blueprint("workout_logs", __name__, url_prefix="/api/v1/workout-logs")


@workout_logs_bp.post("")
@jwt_required()
@swag_from("../docs/workout_logs/log_workout.yml")
def log_workout():
    body, status_code = workout_log_controller.handle_log_workout(
        get_jwt_identity(), request.get_json(silent=True)
    )
    return jsonify(body), status_code


@workout_logs_bp.get("")
@jwt_required()
@swag_from("../docs/workout_logs/get_history.yml")
def get_history():
    body, status_code = workout_log_controller.handle_get_history(get_jwt_identity())
    return jsonify(body), status_code
