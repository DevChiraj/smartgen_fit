"""Auth endpoints - no business logic here, delegates to the controller."""

from flasgger import swag_from
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.controllers import auth_controller

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.post("/register")
@swag_from("../docs/auth/register.yml")
def register():
    body, status_code = auth_controller.handle_register(request.get_json(silent=True))
    return jsonify(body), status_code


@auth_bp.post("/login")
@swag_from("../docs/auth/login.yml")
def login():
    body, status_code = auth_controller.handle_login(request.get_json(silent=True))
    return jsonify(body), status_code


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
@swag_from("../docs/auth/refresh.yml")
def refresh():
    body, status_code = auth_controller.handle_refresh(get_jwt_identity())
    return jsonify(body), status_code


@auth_bp.get("/me")
@jwt_required()
@swag_from("../docs/auth/me.yml")
def me():
    body, status_code = auth_controller.handle_me(get_jwt_identity())
    return jsonify(body), status_code
