"""Stateless BMI calculation and category classification."""

from decimal import ROUND_HALF_UP, Decimal

from app.repositories import bmi_category_repository


def calculate_bmi(height_cm: Decimal, weight_kg: Decimal) -> Decimal:
    height_m = height_cm / Decimal("100")
    bmi = weight_kg / (height_m * height_m)
    return bmi.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def classify_bmi(bmi_value: Decimal):
    return bmi_category_repository.find_category_for_bmi(bmi_value)
