from app.extensions import db as _db
from app.models import (
    AgeGroup,
    BMICategory,
    BodyTypeCategory,
    ImageAnalysisRecord,
    MealRecommendationRecord,
    User,
    UserRecommendation,
)
from app.models.workout_recommendation_record import WorkoutRecommendationRecord


def register_and_get_token(client, username="dash_user"):
    payload = {
        "full_name": "Dashboard User",
        "date_of_birth": "1995-06-15",
        "gender": "female",
        "email": f"{username}@example.com",
        "username": username,
        "password": "supersecret",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    return response.get_json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def seed_reference_tables():
    body_type = BodyTypeCategory(name="Normal", description="Healthy body composition.")
    bmi_category = BMICategory(category_name="Normal weight", min_bmi=18.5, max_bmi=25.0)
    age_group = AgeGroup(name="Adult", min_age=20, max_age=59)
    _db.session.add_all([body_type, bmi_category, age_group])
    _db.session.commit()
    return body_type


def seed_matched_records(db, person_id="MP-TEST"):
    meal_record = MealRecommendationRecord(
        person_id=person_id,
        age=28,
        gender="Female",
        height_cm=165,
        weight_kg=58,
        bmi=21.3,
        bmi_category="Normal",
        breakfast="String hoppers and dhal curry",
        morning_snack="Papaya",
        lunch="Red rice, fish curry, gotu kola sambol",
        evening_snack="Roasted peanuts",
        dinner="Kottu roti",
        daily_calories=1900,
    )
    workout_record = WorkoutRecommendationRecord(
        person_id=person_id,
        age=28,
        gender="Female",
        fitness_level="Intermediate",
        workout_type="Cycling",
        workout_category="Cardio",
        intensity="Moderate",
        duration_min=40,
        days_per_week=4,
        calories_burned=400,
        target_muscle="Full body",
        equipment="Bicycle",
        indoor_outdoor="Outdoor",
        goal="Weight maintenance",
        warmup_min=8,
        cooldown_min=5,
    )
    db.session.add_all([meal_record, workout_record])
    db.session.commit()
    return meal_record, workout_record


def test_latest_recommendation_requires_auth(client, db):
    response = client.get("/api/v1/recommendations/latest")
    assert response.status_code == 401


def test_latest_recommendation_returns_null_when_none_exists(client, db):
    token = register_and_get_token(client)
    response = client.get("/api/v1/recommendations/latest", headers=auth_headers(token))
    assert response.status_code == 200
    assert response.get_json()["recommendation"] is None


def test_latest_recommendation_returns_full_matched_details_when_one_exists(client, db):
    token = register_and_get_token(client)
    user = User.query.filter_by(username="dash_user").first()

    body_type = seed_reference_tables()
    meal_record, workout_record = seed_matched_records(db)

    analysis = ImageAnalysisRecord(
        user_id=user.user_id,
        image_path="uploads/body_images/test.jpg",
        predicted_body_type_id=body_type.body_type_id,
        confidence_score=0.92,
    )
    db.session.add(analysis)
    db.session.commit()

    recommendation = UserRecommendation(
        user_id=user.user_id,
        analysis_id=analysis.analysis_id,
        matched_person_id=meal_record.person_id,
        bmi_value=21.4,
    )
    db.session.add(recommendation)
    db.session.commit()

    response = client.get("/api/v1/recommendations/latest", headers=auth_headers(token))
    assert response.status_code == 200
    body = response.get_json()["recommendation"]

    assert body["bmi_value"] == "21.4"
    assert body["body_type"]["name"] == "Normal"
    assert body["matched_person_id"] == "MP-TEST"
    assert body["meal_record"]["breakfast"] == "String hoppers and dhal curry"
    assert body["meal_record"]["daily_calories"] == 1900
    assert body["workout_record"]["workout_type"] == "Cycling"
    assert body["workout_record"]["calories_burned"] == 400


def test_latest_recommendation_returns_most_recent_of_several(client, db):
    token = register_and_get_token(client)
    user = User.query.filter_by(username="dash_user").first()

    body_type = seed_reference_tables()
    meal_record, _workout_record = seed_matched_records(db)

    older_analysis = ImageAnalysisRecord(
        user_id=user.user_id,
        image_path="a.jpg",
        predicted_body_type_id=body_type.body_type_id,
        confidence_score=0.8,
    )
    newer_analysis = ImageAnalysisRecord(
        user_id=user.user_id,
        image_path="b.jpg",
        predicted_body_type_id=body_type.body_type_id,
        confidence_score=0.9,
    )
    db.session.add_all([older_analysis, newer_analysis])
    db.session.commit()

    older = UserRecommendation(
        user_id=user.user_id,
        analysis_id=older_analysis.analysis_id,
        matched_person_id=meal_record.person_id,
        bmi_value=21.0,
    )
    db.session.add(older)
    db.session.commit()

    newer = UserRecommendation(
        user_id=user.user_id,
        analysis_id=newer_analysis.analysis_id,
        matched_person_id=meal_record.person_id,
        bmi_value=22.0,
    )
    db.session.add(newer)
    db.session.commit()

    other_token = register_and_get_token(client, username="other_user")
    response = client.get("/api/v1/recommendations/latest", headers=auth_headers(other_token))
    # a different user has no recommendations - sanity check isolation
    assert response.get_json()["recommendation"] is None

    response = client.get("/api/v1/recommendations/latest", headers=auth_headers(token))
    assert response.get_json()["recommendation"]["bmi_value"] == "22.0"
