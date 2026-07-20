"""DB access for the workout-recommendation candidate pool (Module 11)."""

from app.models import WorkoutRecommendationRecord


def get_by_person_id(person_id: str) -> WorkoutRecommendationRecord | None:
    return WorkoutRecommendationRecord.query.filter_by(person_id=person_id).first()


def count() -> int:
    return WorkoutRecommendationRecord.query.count()


def bulk_upsert(records: list[dict]) -> None:
    """Idempotent load for the seed command: replace-by-person_id."""
    from app.extensions import db

    existing = {r.person_id: r for r in WorkoutRecommendationRecord.query.all()}
    for data in records:
        row = existing.get(data["person_id"])
        if row is None:
            db.session.add(WorkoutRecommendationRecord(**data))
        else:
            for key, value in data.items():
                setattr(row, key, value)
    db.session.commit()
