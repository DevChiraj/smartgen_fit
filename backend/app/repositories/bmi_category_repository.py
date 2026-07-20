"""DB access for BMI category range lookups."""

from app.extensions import db
from app.models import BMICategory


def get_all() -> list[BMICategory]:
    return BMICategory.query.order_by(BMICategory.min_bmi).all()


def get_by_id(bmi_category_id: int) -> BMICategory | None:
    return db.session.get(BMICategory, bmi_category_id)


def create(**kwargs) -> BMICategory:
    category = BMICategory(**kwargs)
    db.session.add(category)
    db.session.commit()
    return category


def update(category: BMICategory, **kwargs) -> BMICategory:
    for key, value in kwargs.items():
        setattr(category, key, value)
    db.session.commit()
    return category


def delete(category: BMICategory) -> None:
    db.session.delete(category)
    db.session.commit()


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
