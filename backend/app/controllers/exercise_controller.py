"""Request/response orchestration for the public Workouts endpoints."""

from app.schemas.exercise_schema import ExerciseSchema
from app.services import exercise_service

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)


def handle_list(difficulty: str | None, search: str | None):
    exercises = exercise_service.list_exercises(difficulty=difficulty, search=search)
    return {"exercises": exercises_schema.dump(exercises)}, 200


def handle_get(exercise_id: int):
    exercise = exercise_service.get_exercise(exercise_id)
    return {"exercise": exercise_schema.dump(exercise)}, 200


def handle_list_difficulties():
    return {"difficulties": exercise_service.list_difficulties()}, 200
