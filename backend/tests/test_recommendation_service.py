from datetime import date
from decimal import Decimal

import pytest

from app.extensions import db
from app.models import ImageAnalysisRecord, MealRecommendationRecord, User
from app.models.workout_recommendation_record import WorkoutRecommendationRecord
from app.services import recommendation_service
from app.utils.exceptions import AppError


def _make_user(height_cm=None, weight_kg=None):
    user = User(
        full_name="Test User",
        date_of_birth=date(1995, 1, 1),
        age=29,
        gender="female",
        email="reco_test@example.com",
        username="reco_test_user",
        password_hash="x",
        height_cm=height_cm,
        weight_kg=weight_kg,
    )
    db.session.add(user)
    db.session.commit()
    return user


def _seed_meal_record(person_id="P001", bmi=24.0):
    record = MealRecommendationRecord(
        person_id=person_id,
        age=29,
        gender="Female",
        height_cm=165,
        weight_kg=65,
        bmi=bmi,
        bmi_category="Normal",
        breakfast="Oats",
        morning_snack="Fruit",
        lunch="Rice and curry",
        evening_snack="Nuts",
        dinner="Soup",
        daily_calories=2000,
    )
    db.session.add(record)
    db.session.commit()
    return record


def _seed_workout_record(person_id="P001"):
    record = WorkoutRecommendationRecord(
        person_id=person_id,
        age=29,
        gender="Female",
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
    db.session.add(record)
    db.session.commit()
    return record


def test_match_recommendation_raises_500_when_matched_person_has_no_meal_record(
    app, db, monkeypatch
):
    user = _make_user()
    monkeypatch.setattr(
        "app.services.recommendation_service.ml_recommendation.find_matching_person",
        lambda label, age, gender: "GHOST",
    )

    with pytest.raises(AppError) as exc_info:
        recommendation_service.match_recommendation(user, "normal")
    assert exc_info.value.status_code == 500
    assert "GHOST" in exc_info.value.message


def test_match_recommendation_raises_500_when_matched_person_has_no_workout_record(
    app, db, monkeypatch
):
    user = _make_user()
    _seed_meal_record("P001")
    monkeypatch.setattr(
        "app.services.recommendation_service.ml_recommendation.find_matching_person",
        lambda label, age, gender: "P001",
    )

    with pytest.raises(AppError) as exc_info:
        recommendation_service.match_recommendation(user, "normal")
    assert exc_info.value.status_code == 500
    assert "workout_recommendation_records" in exc_info.value.message


def test_match_recommendation_succeeds_when_both_records_exist(app, db, monkeypatch):
    user = _make_user()
    _seed_meal_record("P001")
    _seed_workout_record("P001")
    monkeypatch.setattr(
        "app.services.recommendation_service.ml_recommendation.find_matching_person",
        lambda label, age, gender: "P001",
    )

    match = recommendation_service.match_recommendation(user, "normal")
    assert match.meal_record.person_id == "P001"
    assert match.workout_record.person_id == "P001"


def test_save_recommendation_uses_users_own_bmi_when_profile_is_complete(app, db):
    user = _make_user(height_cm=170, weight_kg=65)
    meal_record = _seed_meal_record("P001", bmi=30.0)
    workout_record = _seed_workout_record("P001")
    analysis = ImageAnalysisRecord(
        user_id=user.user_id,
        image_path="x.jpg",
        predicted_body_type_id=1,
        confidence_score=0.9,
    )
    db.session.add(analysis)
    db.session.commit()

    match = recommendation_service.RecommendationMatch(
        meal_record=meal_record, workout_record=workout_record
    )
    saved = recommendation_service.save_recommendation(user, analysis, match)

    # 65 / (1.70^2) = 22.5, not the matched record's 30.0
    assert saved.bmi_value == Decimal("22.5")


def test_save_recommendation_falls_back_to_matched_bmi_when_profile_incomplete(app, db):
    user = _make_user(height_cm=None, weight_kg=None)
    meal_record = _seed_meal_record("P001", bmi=27.4)
    workout_record = _seed_workout_record("P001")
    analysis = ImageAnalysisRecord(
        user_id=user.user_id,
        image_path="x.jpg",
        predicted_body_type_id=1,
        confidence_score=0.9,
    )
    db.session.add(analysis)
    db.session.commit()

    match = recommendation_service.RecommendationMatch(
        meal_record=meal_record, workout_record=workout_record
    )
    saved = recommendation_service.save_recommendation(user, analysis, match)

    assert saved.bmi_value == Decimal("27.4")
