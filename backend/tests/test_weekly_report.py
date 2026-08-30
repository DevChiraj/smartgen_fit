from datetime import date, timedelta

from app.extensions import db as _db
from app.models import (
    AgeGroup,
    BMICategory,
    BodyTypeCategory,
    Exercise,
    ImageAnalysisRecord,
    MealRecommendationRecord,
    SriLankanFood,
    User,
    UserRecommendation,
)
from app.models.workout_recommendation_record import WorkoutRecommendationRecord


def register_and_get_token(client, username="report_user"):
    payload = {
        "full_name": "Report User",
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


def seed_matched_records(person_id="MP-TEST"):
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
    _db.session.add_all([meal_record, workout_record])
    _db.session.commit()
    return meal_record, workout_record


def seed_exercise():
    exercise = Exercise(
        exercise_name="Push Up",
        target_muscle="Chest",
        difficulty="Beginner",
        equipment=None,
        sets=3,
        reps=15,
        calories_per_30min=180,
        benefit="Builds upper body strength.",
    )
    _db.session.add(exercise)
    _db.session.commit()
    return exercise


def seed_food():
    food = SriLankanFood(
        food_name="Chicken Curry",
        category="Protein",
        serving_size="100g",
        calories=190,
        protein_g=24,
        carbs_g=4,
        fat_g=9,
    )
    _db.session.add(food)
    _db.session.commit()
    return food


def test_weekly_report_requires_auth(client, db):
    response = client.get("/api/v1/reports/weekly")
    assert response.status_code == 401


def test_weekly_report_for_a_brand_new_user_has_no_bmi_scan_or_recommendation(client, db):
    token = register_and_get_token(client)
    response = client.get("/api/v1/reports/weekly", headers=auth_headers(token))
    assert response.status_code == 200
    report = response.get_json()["report"]

    assert report["user"]["full_name"] == "Report User"
    assert report["bmi_value"] is None
    assert report["bmi_category"] is None
    assert report["latest_analysis"] is None
    assert report["recommendation"] is None
    assert report["totals"]["calories_consumed"] == 0
    assert report["totals"]["calories_burned"] == 0
    assert report["totals"]["workouts_logged"] == 0
    assert report["totals"]["meals_logged"] == 0


def test_weekly_report_computes_bmi_from_profile_height_and_weight(client, db):
    token = register_and_get_token(client)
    seed_reference_tables()
    client.put(
        "/api/v1/users/me",
        headers=auth_headers(token),
        json={"height_cm": 170, "weight_kg": 65},
    )

    response = client.get("/api/v1/reports/weekly", headers=auth_headers(token))
    report = response.get_json()["report"]
    assert report["bmi_value"] == "22.5"
    assert report["bmi_category"]["category_name"] == "Normal weight"


def test_weekly_report_includes_latest_scan_and_recommendation(client, db):
    token = register_and_get_token(client)
    user = User.query.filter_by(username="report_user").first()
    body_type = seed_reference_tables()
    meal_record, workout_record = seed_matched_records()

    analysis = ImageAnalysisRecord(
        user_id=user.user_id,
        image_path="uploads/body_images/test.jpg",
        predicted_body_type_id=body_type.body_type_id,
        confidence_score=0.92,
    )
    _db.session.add(analysis)
    _db.session.commit()

    recommendation = UserRecommendation(
        user_id=user.user_id,
        analysis_id=analysis.analysis_id,
        matched_person_id=meal_record.person_id,
        bmi_value=21.4,
    )
    _db.session.add(recommendation)
    _db.session.commit()

    response = client.get("/api/v1/reports/weekly", headers=auth_headers(token))
    report = response.get_json()["report"]
    assert report["latest_analysis"]["predicted_body_type"]["name"] == "Normal"
    assert report["recommendation"]["meal_record"]["daily_calories"] == 1900
    assert report["recommendation"]["workout_record"]["workout_type"] == "Cycling"


def test_weekly_report_totals_only_include_the_last_seven_days(client, db):
    token = register_and_get_token(client)
    exercise = seed_exercise()
    food = seed_food()

    today = date.today()
    within_window = (today - timedelta(days=3)).isoformat()
    outside_window = (today - timedelta(days=10)).isoformat()

    client.post(
        "/api/v1/workout-logs",
        headers=auth_headers(token),
        json={
            "exercise_id": exercise.exercise_id,
            "duration_minutes": 30,
            "log_date": within_window,
        },
    )
    client.post(
        "/api/v1/workout-logs",
        headers=auth_headers(token),
        json={
            "exercise_id": exercise.exercise_id,
            "duration_minutes": 30,
            "log_date": outside_window,
        },
    )
    client.post(
        "/api/v1/meal-logs",
        headers=auth_headers(token),
        json={"food_id": food.food_id, "meal_type": "lunch", "log_date": within_window},
    )
    client.post(
        "/api/v1/meal-logs",
        headers=auth_headers(token),
        json={"food_id": food.food_id, "meal_type": "lunch", "log_date": outside_window},
    )

    response = client.get("/api/v1/reports/weekly", headers=auth_headers(token))
    totals = response.get_json()["report"]["totals"]
    assert totals["workouts_logged"] == 1
    assert totals["meals_logged"] == 1
    assert totals["calories_burned"] == 180  # 180 kcal/30min * 30 min
    assert totals["calories_consumed"] == 190
    assert totals["protein_g"] == "24.00"


def test_weekly_report_isolates_totals_per_user(client, db):
    token_a = register_and_get_token(client, username="user_a")
    token_b = register_and_get_token(client, username="user_b")
    exercise = seed_exercise()

    client.post(
        "/api/v1/workout-logs",
        headers=auth_headers(token_a),
        json={"exercise_id": exercise.exercise_id, "duration_minutes": 30},
    )

    response = client.get("/api/v1/reports/weekly", headers=auth_headers(token_b))
    totals = response.get_json()["report"]["totals"]
    assert totals["workouts_logged"] == 0
    assert totals["calories_burned"] == 0
