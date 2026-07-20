"""Read-only nutrition lookup - public data, no AI or recommendation
logic involved. Kept fully separate from RecommendationService: this is
plain reference data browsing (the "Healthy Foods" page), not part of
the Module 11 matching pipeline.
"""

from app.models import SriLankanFood
from app.repositories import food_repository
from app.utils.exceptions import NotFoundError


def list_foods(category: str | None = None, search: str | None = None) -> list[SriLankanFood]:
    return food_repository.get_all(category=category, search=search)


def get_food(food_id: int) -> SriLankanFood:
    food = food_repository.get_by_id(food_id)
    if food is None:
        raise NotFoundError(f"No food found with id {food_id}.")
    return food


def list_categories() -> list[str]:
    return food_repository.get_categories()
