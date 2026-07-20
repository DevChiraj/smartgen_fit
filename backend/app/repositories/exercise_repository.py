"""DB access for the exercises reference library."""

from sqlalchemy import func

from app.extensions import db
from app.models import Exercise


def get_all(difficulty: str | None = None, search: str | None = None) -> list[Exercise]:
    query = Exercise.query
    if difficulty:
        query = query.filter(func.lower(Exercise.difficulty) == difficulty.lower())
    if search:
        query = query.filter(Exercise.exercise_name.ilike(f"%{search}%"))
    return query.order_by(Exercise.exercise_name).all()


def get_by_id(exercise_id: int) -> Exercise | None:
    return db.session.get(Exercise, exercise_id)


def get_difficulties() -> list[str]:
    rows = Exercise.query.with_entities(Exercise.difficulty).distinct().all()
    return sorted(row[0] for row in rows)
