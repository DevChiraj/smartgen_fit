"""Business logic for the meal diary: log a food entry against a real
sri_lankan_foods row, deriving calories and protein at log time from that
food's nutrition data times the servings eaten.
"""

from datetime import date
from decimal import Decimal

from app.models import MealLog
from app.repositories import food_repository, meal_log_repository
from app.utils.exceptions import NotFoundError


def log_meal(
    user_id: int,
    food_id: int,
    meal_type: str,
    quantity_servings: Decimal,
    log_date: date | None,
    notes: str | None,
) -> MealLog:
    food = food_repository.get_by_id(food_id)
    if food is None:
        raise NotFoundError(f"No food with id {food_id}.")

    calories = round(food.calories * quantity_servings)
    protein_g = (food.protein_g * quantity_servings).quantize(Decimal("0.01"))

    return meal_log_repository.create(
        user_id=user_id,
        food_id=food_id,
        meal_type=meal_type,
        log_date=log_date or date.today(),
        quantity_servings=quantity_servings,
        calories=calories,
        protein_g=protein_g,
        notes=notes,
    )


def get_history(user_id: int) -> list[MealLog]:
    return meal_log_repository.get_history_for_user(user_id)
