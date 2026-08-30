"""DB access for the meal-recommendation candidate pool (Module 11)."""

from app.models import MealRecommendationRecord


def get_by_person_id(person_id: str) -> MealRecommendationRecord | None:
    return MealRecommendationRecord.query.filter_by(person_id=person_id).first()


def count() -> int:
    return MealRecommendationRecord.query.count()


def bulk_upsert(records: list[dict]) -> None:
    """Idempotent load for the seed command: replace-by-person_id."""
    from app.extensions import db

    existing = {r.person_id: r for r in MealRecommendationRecord.query.all()}
    for data in records:
        row = existing.get(data["person_id"])
        if row is None:
            db.session.add(MealRecommendationRecord(**data))
        else:
            for key, value in data.items():
                setattr(row, key, value)
    db.session.commit()
