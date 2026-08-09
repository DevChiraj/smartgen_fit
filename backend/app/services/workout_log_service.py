"""Business logic for the workout tracker: log a completed workout against a
real exercises row, auto-filling calories burned from the exercise's
reference rate when the user doesn't provide their own.
"""

from datetime import date

from app.models import WorkoutLog
from app.repositories import exercise_repository, workout_log_repository
from app.utils.exceptions import NotFoundError


def log_workout(
    user_id: int,
    exercise_id: int,
    duration_minutes: int,
    log_date: date | None,
    calories_burned: int | None,
    notes: str | None,
) -> WorkoutLog:
    exercise = exercise_repository.get_by_id(exercise_id)
    if exercise is None:
        raise NotFoundError(f"No exercise with id {exercise_id}.")

    if calories_burned is None:
        calories_burned = round(exercise.calories_per_30min * duration_minutes / 30)

    return workout_log_repository.create(
        user_id=user_id,
        exercise_id=exercise_id,
        log_date=log_date or date.today(),
        duration_minutes=duration_minutes,
        calories_burned=calories_burned,
        notes=notes,
    )


def get_history(user_id: int) -> list[WorkoutLog]:
    return workout_log_repository.get_history_for_user(user_id)
