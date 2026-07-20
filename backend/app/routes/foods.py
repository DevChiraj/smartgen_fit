"""Food endpoints - public (no auth), no business logic here, delegates to
the controller.
"""

from flask import Blueprint, jsonify, request

from app.controllers import food_controller

foods_bp = Blueprint("foods", __name__, url_prefix="/api/v1/foods")


@foods_bp.get("")
def list_foods():
    category = request.args.get("category")
    search = request.args.get("q")
    body, status_code = food_controller.handle_list(category, search)
    return jsonify(body), status_code


@foods_bp.get("/categories")
def list_categories():
    body, status_code = food_controller.handle_list_categories()
    return jsonify(body), status_code


@foods_bp.get("/<int:food_id>")
def get_food(food_id):
    body, status_code = food_controller.handle_get(food_id)
    return jsonify(body), status_code
