"""Profile endpoints - no business logic here, delegates to the controller."""

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.controllers import user_controller

users_bp = Blueprint("users", __name__, url_prefix="/api/v1/users")


@users_bp.get("/me")
@jwt_required()
def get_me():
    body, status_code = user_controller.handle_get_me(get_jwt_identity())
    return jsonify(body), status_code


@users_bp.put("/me")
@jwt_required()
def update_me():
    body, status_code = user_controller.handle_update_me(
        get_jwt_identity(), request.get_json(silent=True)
    )
    return jsonify(body), status_code


@users_bp.post("/me/profile-picture")
@jwt_required()
def upload_profile_picture():
    file = request.files.get("profile_picture")
    body, status_code = user_controller.handle_upload_profile_picture(get_jwt_identity(), file)
    return jsonify(body), status_code


@users_bp.get("/uploads/profile-pictures/<path:filename>")
def serve_profile_picture(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
