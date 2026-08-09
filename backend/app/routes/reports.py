"""Weekly health report endpoint - no business logic here, delegates to the controller."""

from flasgger import swag_from
from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.controllers import report_controller

reports_bp = Blueprint("reports", __name__, url_prefix="/api/v1/reports")


@reports_bp.get("/weekly")
@jwt_required()
@swag_from("../docs/reports/weekly.yml")
def weekly_report():
    body, status_code = report_controller.handle_get_weekly_report(get_jwt_identity())
    return jsonify(body), status_code
