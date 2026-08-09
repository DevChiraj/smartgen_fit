"""Request/response orchestration for the meal diary endpoints."""

from app.schemas.meal_log_schema import MealLogCreateSchema, MealLogSchema
from app.services import meal_log_service

create_schema = MealLogCreateSchema()
log_schema = MealLogSchema()
logs_schema = MealLogSchema(many=True)


def handle_log_meal(user_id: str, json_body):
    data = create_schema.load(json_body or {})
    log = meal_log_service.log_meal(
        user_id=int(user_id),
        food_id=data["food_id"],
        meal_type=data["meal_type"],
        quantity_servings=data["quantity_servings"],
        log_date=data.get("log_date"),
        notes=data.get("notes"),
    )
    return {"log": log_schema.dump(log)}, 201


def handle_get_history(user_id: str):
    logs = meal_log_service.get_history(int(user_id))
    return {"history": logs_schema.dump(logs)}, 200
