"""Recommendation endpoints - no business logic here, delegates to the controller."""

from flasgger import swag_from
from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.controllers import recommendation_controller

recommendations_bp = Blueprint("recommendations", __name__, url_prefix="/api/v1/recommendations")


@recommendations_bp.get("/latest")
@jwt_required()
@swag_from("../docs/recommendations/latest.yml")
def latest():
    body, status_code = recommendation_controller.handle_get_latest(get_jwt_identity())
    return jsonify(body), status_code
