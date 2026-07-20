"""Exercise endpoints - public (no auth), no business logic here, delegates
to the controller.
"""

from flask import Blueprint, jsonify, request

from app.controllers import exercise_controller

exercises_bp = Blueprint("exercises", __name__, url_prefix="/api/v1/exercises")


@exercises_bp.get("")
def list_exercises():
    difficulty = request.args.get("difficulty")
    search = request.args.get("q")
    body, status_code = exercise_controller.handle_list(difficulty, search)
    return jsonify(body), status_code


@exercises_bp.get("/difficulties")
def list_difficulties():
    body, status_code = exercise_controller.handle_list_difficulties()
    return jsonify(body), status_code


@exercises_bp.get("/<int:exercise_id>")
def get_exercise(exercise_id):
    body, status_code = exercise_controller.handle_get(exercise_id)
    return jsonify(body), status_code
