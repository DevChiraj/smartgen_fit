from app.models import MealRecommendationRecord
from app.repositories import workout_recommendation_repository
from app.extensions import db


def _seed_meal_record(person_id):
    db.session.add(
        MealRecommendationRecord(
            person_id=person_id,
            age=30,
            gender="Male",
            height_cm=175,
            weight_kg=70,
            bmi=22.9,
            bmi_category="Normal",
            breakfast="Oats",
            morning_snack="Fruit",
            lunch="Rice and curry",
            evening_snack="Nuts",
            dinner="Soup",
            daily_calories=2000,
        )
    )
    db.session.commit()


def _record(person_id="P001", **overrides):
    data = dict(
        person_id=person_id,
        age=30,
        gender="Male",
        fitness_level="Intermediate",
        workout_type="Cardio",
        workout_category="Cardio",
        intensity="Moderate",
        duration_min=30,
        days_per_week=3,
        calories_burned=250,
        target_muscle="Full Body",
        equipment=None,
        indoor_outdoor="Indoor",
        goal="Maintenance",
        warmup_min=5,
        cooldown_min=5,
    )
    data.update(overrides)
    return data


def test_count_is_zero_when_empty(app, db):
    assert workout_recommendation_repository.count() == 0


def test_bulk_upsert_creates_new_records(app, db):
    _seed_meal_record("P001")
    _seed_meal_record("P002")

    workout_recommendation_repository.bulk_upsert([_record("P001"), _record("P002")])

    assert workout_recommendation_repository.count() == 2
    assert workout_recommendation_repository.get_by_person_id("P001").duration_min == 30


def test_bulk_upsert_updates_existing_records_by_person_id(app, db):
    _seed_meal_record("P001")
    workout_recommendation_repository.bulk_upsert([_record("P001", duration_min=30)])
    workout_recommendation_repository.bulk_upsert(
        [_record("P001", duration_min=45, workout_type="Strength")]
    )

    assert workout_recommendation_repository.count() == 1
    updated = workout_recommendation_repository.get_by_person_id("P001")
    assert updated.duration_min == 45
    assert updated.workout_type == "Strength"


def test_bulk_upsert_is_idempotent(app, db):
    for person_id in ("P001", "P002", "P003"):
        _seed_meal_record(person_id)
    records = [_record("P001"), _record("P002"), _record("P003")]

    workout_recommendation_repository.bulk_upsert(records)
    workout_recommendation_repository.bulk_upsert(records)

    assert workout_recommendation_repository.count() == 3


def test_get_by_person_id_returns_none_when_missing(app, db):
    assert workout_recommendation_repository.get_by_person_id("NOPE") is None
