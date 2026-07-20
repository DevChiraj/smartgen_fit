"""Admin-only BMI category management (thresholds, add/remove ranges).
Separate from bmi_service.py, which is the calculation-facing service
(stateless BMI + category lookup) - this is CRUD over the same table.
"""

from app.models import BMICategory
from app.repositories import bmi_category_repository
from app.utils.exceptions import AppError, NotFoundError


class LastCategoryError(AppError):
    status_code = 409


def list_categories() -> list[BMICategory]:
    return bmi_category_repository.get_all()


def get_category(bmi_category_id: int) -> BMICategory:
    category = bmi_category_repository.get_by_id(bmi_category_id)
    if category is None:
        raise NotFoundError(f"No BMI category found with id {bmi_category_id}.")
    return category


def create_category(data: dict) -> BMICategory:
    return bmi_category_repository.create(**data)


def update_category(bmi_category_id: int, data: dict) -> BMICategory:
    category = get_category(bmi_category_id)
    return bmi_category_repository.update(category, **data)


def delete_category(bmi_category_id: int) -> None:
    category = get_category(bmi_category_id)
    if len(bmi_category_repository.get_all()) <= 1:
        raise LastCategoryError(
            "Cannot delete the last BMI category - the BMI calculator needs at least one."
        )
    bmi_category_repository.delete(category)
