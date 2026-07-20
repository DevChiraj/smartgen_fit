"""Admin-only endpoints - every route here requires the "admin" role
(role_required, backend/app/utils/decorators.py). No business logic
here, delegates to admin_controller.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.controllers import admin_controller
from app.utils.decorators import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


# --- Users ---


@admin_bp.get("/users")
@role_required("admin")
def list_users():
    body, status_code = admin_controller.handle_list_users()
    return jsonify(body), status_code


@admin_bp.get("/users/<int:user_id>")
@role_required("admin")
def get_user(user_id):
    body, status_code = admin_controller.handle_get_user(user_id)
    return jsonify(body), status_code


@admin_bp.put("/users/<int:user_id>")
@role_required("admin")
def update_user(user_id):
    body, status_code = admin_controller.handle_update_user(user_id, request.get_json(silent=True))
    return jsonify(body), status_code


@admin_bp.delete("/users/<int:user_id>")
@role_required("admin")
def delete_user(user_id):
    body, status_code = admin_controller.handle_delete_user(user_id, int(get_jwt_identity()))
    return jsonify(body), status_code


# --- Foods ---


@admin_bp.post("/foods")
@role_required("admin")
def create_food():
    body, status_code = admin_controller.handle_create_food(request.get_json(silent=True))
    return jsonify(body), status_code


@admin_bp.put("/foods/<int:food_id>")
@role_required("admin")
def update_food(food_id):
    body, status_code = admin_controller.handle_update_food(food_id, request.get_json(silent=True))
    return jsonify(body), status_code


@admin_bp.delete("/foods/<int:food_id>")
@role_required("admin")
def delete_food(food_id):
    body, status_code = admin_controller.handle_delete_food(food_id)
    return jsonify(body), status_code


# --- Exercises ---


@admin_bp.post("/exercises")
@role_required("admin")
def create_exercise():
    body, status_code = admin_controller.handle_create_exercise(request.get_json(silent=True))
    return jsonify(body), status_code


@admin_bp.put("/exercises/<int:exercise_id>")
@role_required("admin")
def update_exercise(exercise_id):
    body, status_code = admin_controller.handle_update_exercise(
        exercise_id, request.get_json(silent=True)
    )
    return jsonify(body), status_code


@admin_bp.delete("/exercises/<int:exercise_id>")
@role_required("admin")
def delete_exercise(exercise_id):
    body, status_code = admin_controller.handle_delete_exercise(exercise_id)
    return jsonify(body), status_code


# --- Body types ---


@admin_bp.get("/body-types")
@role_required("admin")
def list_body_types():
    body, status_code = admin_controller.handle_list_body_types()
    return jsonify(body), status_code


@admin_bp.put("/body-types/<int:body_type_id>")
@role_required("admin")
def update_body_type(body_type_id):
    body, status_code = admin_controller.handle_update_body_type(
        body_type_id, request.get_json(silent=True)
    )
    return jsonify(body), status_code


# --- BMI categories ---


@admin_bp.get("/bmi-categories")
@role_required("admin")
def list_bmi_categories():
    body, status_code = admin_controller.handle_list_bmi_categories()
    return jsonify(body), status_code


@admin_bp.post("/bmi-categories")
@role_required("admin")
def create_bmi_category():
    body, status_code = admin_controller.handle_create_bmi_category(request.get_json(silent=True))
    return jsonify(body), status_code


@admin_bp.put("/bmi-categories/<int:bmi_category_id>")
@role_required("admin")
def update_bmi_category(bmi_category_id):
    body, status_code = admin_controller.handle_update_bmi_category(
        bmi_category_id, request.get_json(silent=True)
    )
    return jsonify(body), status_code


@admin_bp.delete("/bmi-categories/<int:bmi_category_id>")
@role_required("admin")
def delete_bmi_category(bmi_category_id):
    body, status_code = admin_controller.handle_delete_bmi_category(bmi_category_id)
    return jsonify(body), status_code
