"""Request/response orchestration for the BMI calculator."""

from app.schemas.bmi_schema import BMICalculateSchema, BMICategorySchema
from app.services import bmi_service

bmi_calculate_schema = BMICalculateSchema()
bmi_category_schema = BMICategorySchema()


def handle_calculate(json_body):
    data = bmi_calculate_schema.load(json_body or {})
    bmi_value = bmi_service.calculate_bmi(data["height_cm"], data["weight_kg"])
    category = bmi_service.classify_bmi(bmi_value)

    return {
        "bmi": str(bmi_value),
        "category": bmi_category_schema.dump(category) if category else None,
    }, 200
