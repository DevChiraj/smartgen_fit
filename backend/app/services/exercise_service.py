"""Read-only exercise library lookup - public data, no AI or recommendation
logic involved. Fully separate from RecommendationService: this is plain
reference content (the "Workouts" page), not part of the Module 11
matching pipeline.
"""

from app.models import Exercise
from app.repositories import exercise_repository
from app.utils.exceptions import NotFoundError


def list_exercises(difficulty: str | None = None, search: str | None = None) -> list[Exercise]:
    return exercise_repository.get_all(difficulty=difficulty, search=search)


def get_exercise(exercise_id: int) -> Exercise:
    exercise = exercise_repository.get_by_id(exercise_id)
    if exercise is None:
        raise NotFoundError(f"No exercise found with id {exercise_id}.")
    return exercise


def list_difficulties() -> list[str]:
    return exercise_repository.get_difficulties()
