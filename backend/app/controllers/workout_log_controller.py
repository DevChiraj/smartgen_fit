"""Request/response orchestration for the workout tracker endpoints."""

from app.schemas.workout_log_schema import WorkoutLogCreateSchema, WorkoutLogSchema
from app.services import workout_log_service

create_schema = WorkoutLogCreateSchema()
log_schema = WorkoutLogSchema()
logs_schema = WorkoutLogSchema(many=True)


def handle_log_workout(user_id: str, json_body):
    data = create_schema.load(json_body or {})
    log = workout_log_service.log_workout(
        user_id=int(user_id),
        exercise_id=data["exercise_id"],
        duration_minutes=data["duration_minutes"],
        log_date=data.get("log_date"),
        calories_burned=data.get("calories_burned"),
        notes=data.get("notes"),
    )
    return {"log": log_schema.dump(log)}, 201


def handle_get_history(user_id: str):
    logs = workout_log_service.get_history(int(user_id))
    return {"history": logs_schema.dump(logs)}, 200
