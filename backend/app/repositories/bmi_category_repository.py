"""DB access for BMI category range lookups."""

from app.models import BMICategory


def find_category_for_bmi(bmi_value) -> BMICategory | None:
    category = (
        BMICategory.query.filter(BMICategory.min_bmi <= bmi_value, BMICategory.max_bmi > bmi_value)
        .order_by(BMICategory.min_bmi)
        .first()
    )
    if category is not None:
        return category

    # BMI at or above the highest defined range (e.g. above "Obese") still
    # belongs to that top category - ranges are open-ended upward.
    return BMICategory.query.order_by(BMICategory.min_bmi.desc()).first()
