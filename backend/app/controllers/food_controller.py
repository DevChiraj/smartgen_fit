"""Request/response orchestration for the public Healthy Foods endpoints."""

from app.schemas.food_schema import SriLankanFoodSchema
from app.services import food_service

food_schema = SriLankanFoodSchema()
foods_schema = SriLankanFoodSchema(many=True)


def handle_list(category: str | None, search: str | None):
    foods = food_service.list_foods(category=category, search=search)
    return {"foods": foods_schema.dump(foods)}, 200


def handle_get(food_id: int):
    food = food_service.get_food(food_id)
    return {"food": food_schema.dump(food)}, 200


def handle_list_categories():
    return {"categories": food_service.list_categories()}, 200
