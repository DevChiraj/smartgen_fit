from app.repositories import meal_recommendation_repository


def _record(person_id="P001", **overrides):
    data = dict(
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
    data.update(overrides)
    return data


def test_count_is_zero_when_empty(app, db):
    assert meal_recommendation_repository.count() == 0


def test_bulk_upsert_creates_new_records(app, db):
    meal_recommendation_repository.bulk_upsert([_record("P001"), _record("P002")])

    assert meal_recommendation_repository.count() == 2
    assert meal_recommendation_repository.get_by_person_id("P001").daily_calories == 2000


def test_bulk_upsert_updates_existing_records_by_person_id(app, db):
    meal_recommendation_repository.bulk_upsert([_record("P001", daily_calories=2000)])
    meal_recommendation_repository.bulk_upsert(
        [_record("P001", daily_calories=2500, breakfast="Eggs")]
    )

    assert meal_recommendation_repository.count() == 1
    updated = meal_recommendation_repository.get_by_person_id("P001")
    assert updated.daily_calories == 2500
    assert updated.breakfast == "Eggs"


def test_bulk_upsert_is_idempotent(app, db):
    records = [_record("P001"), _record("P002"), _record("P003")]
    meal_recommendation_repository.bulk_upsert(records)
    meal_recommendation_repository.bulk_upsert(records)

    assert meal_recommendation_repository.count() == 3


def test_get_by_person_id_returns_none_when_missing(app, db):
    assert meal_recommendation_repository.get_by_person_id("NOPE") is None
