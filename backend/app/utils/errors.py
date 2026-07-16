"""Centralized JSON error handlers: {error, message, status} on every failure."""

from flask import jsonify
from werkzeug.exceptions import HTTPException


def _json_error(error: str, message: str, status: int):
    response = jsonify({"error": error, "message": message, "status": status})
    response.status_code = status
    return response


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(exc: HTTPException):
        return _json_error(exc.name, exc.description, exc.code)

    @app.errorhandler(Exception)
    def handle_unexpected_exception(exc: Exception):
        app.logger.exception("Unhandled exception")
        return _json_error("Internal Server Error", "An unexpected error occurred.", 500)
