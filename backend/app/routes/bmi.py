"""BMI calculator endpoint - stateless utility, public, no auth required."""

from flask import Blueprint, jsonify, request

from app.controllers import bmi_controller

bmi_bp = Blueprint("bmi", __name__, url_prefix="/api/v1/bmi")


@bmi_bp.post("/calculate")
def calculate():
    body, status_code = bmi_controller.handle_calculate(request.get_json(silent=True))
    return jsonify(body), status_code
