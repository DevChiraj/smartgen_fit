"""Image analysis endpoints - no business logic here, delegates to the controller."""

from flasgger import swag_from
from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.controllers import image_analysis_controller

image_analysis_bp = Blueprint("image_analysis", __name__, url_prefix="/api/v1/image-analysis")


@image_analysis_bp.post("")
@jwt_required()
@swag_from("../docs/image_analysis/analyze.yml")
def analyze():
    file = request.files.get("image")
    body, status_code = image_analysis_controller.handle_analyze(get_jwt_identity(), file)
    return jsonify(body), status_code


@image_analysis_bp.get("/history")
@jwt_required()
@swag_from("../docs/image_analysis/history.yml")
def history():
    body, status_code = image_analysis_controller.handle_get_history(get_jwt_identity())
    return jsonify(body), status_code


@image_analysis_bp.get("/uploads/<path:filename>")
@swag_from("../docs/image_analysis/serve_uploaded_image.yml")
def serve_uploaded_image(filename):
    return send_from_directory(current_app.config["BODY_IMAGE_UPLOAD_FOLDER"], filename)
