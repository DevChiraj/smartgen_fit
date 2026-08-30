"""Centralized JSON error handlers: {error, message, status} on every failure."""

from flask import jsonify
from marshmallow import ValidationError as SchemaValidationError
from werkzeug.exceptions import HTTPException

from app.utils.exceptions import AppError


def _json_error(error: str, message, status: int):
    response = jsonify({"error": error, "message": message, "status": status})
    response.status_code = status
    return response


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(exc: HTTPException):
        return _json_error(exc.name, exc.description, exc.code)

    @app.errorhandler(AppError)
    def handle_app_error(exc: AppError):
        return _json_error(type(exc).__name__, exc.message, exc.status_code)

    @app.errorhandler(SchemaValidationError)
    def handle_schema_validation_error(exc: SchemaValidationError):
        return _json_error("ValidationError", exc.messages, 400)

    @app.errorhandler(Exception)
    def handle_unexpected_exception(exc: Exception):
        app.logger.exception("Unhandled exception")
        return _json_error("Internal Server Error", "An unexpected error occurred.", 500)


def register_jwt_error_handlers(jwt_manager):
    """Make Flask-JWT-Extended's built-in error responses match our {error, message, status}."""

    @jwt_manager.unauthorized_loader
    def handle_missing_token(reason):
        return _json_error("Unauthorized", reason, 401)

    @jwt_manager.invalid_token_loader
    def handle_invalid_token(reason):
        return _json_error("Unauthorized", reason, 401)

    @jwt_manager.expired_token_loader
    def handle_expired_token(jwt_header, jwt_payload):
        return _json_error("Unauthorized", "Token has expired.", 401)

    @jwt_manager.needs_fresh_token_loader
    def handle_needs_fresh_token(jwt_header, jwt_payload):
        return _json_error("Unauthorized", "Fresh token required.", 401)

    @jwt_manager.revoked_token_loader
    def handle_revoked_token(jwt_header, jwt_payload):
        return _json_error("Unauthorized", "Token has been revoked.", 401)
