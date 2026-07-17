from app.models import (
    AgeGroup,
    BMICategory,
    BodyTypeCategory,
    ImageAnalysisRecord,
    MealPlan,
    User,
    UserRecommendation,
    WorkoutPlan,
)


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


def test_latest_recommendation_requires_auth(client, db):
    response = client.get("/api/v1/recommendations/latest")
    assert response.status_code == 401


def test_latest_recommendation_returns_null_when_none_exists(client, db):
    token = register_and_get_token(client)
    response = client.get("/api/v1/recommendations/latest", headers=auth_headers(token))
    assert response.status_code == 200
    assert response.get_json()["recommendation"] is None


def test_latest_recommendation_returns_full_summary_when_one_exists(client, db):
    token = register_and_get_token(client)
    user = User.query.filter_by(username="dash_user").first()

    body_type = BodyTypeCategory(name="Normal", description="Healthy body composition.")
    bmi_category = BMICategory(category_name="Normal weight", min_bmi=18.5, max_bmi=25.0)
    age_group = AgeGroup(name="Adult", min_age=20, max_age=59)
    db.session.add_all([body_type, bmi_category, age_group])
    db.session.commit()

    meal_plan = MealPlan(
        plan_code="MP-TEST",
        body_type_id=body_type.body_type_id,
        bmi_category_id=bmi_category.bmi_category_id,
        age_group_id=age_group.age_group_id,
        gender="female",
        breakfast="x",
        lunch="x",
        dinner="x",
        calories=1900,
        protein_g=75,
        carbs_g=240,
        fat_g=55,
    )
    workout_plan = WorkoutPlan(
        plan_code="WP-TEST",
        body_type_id=body_type.body_type_id,
        bmi_category_id=bmi_category.bmi_category_id,
        age_group_id=age_group.age_group_id,
        gender="female",
        warm_up="x",
        cardio="x",
        strength_training="x",
        stretching="x",
        cool_down="x",
        duration_minutes=55,
        calories_burned=400,
    )
    db.session.add_all([meal_plan, workout_plan])
    db.session.commit()

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
        meal_plan_id=meal_plan.meal_plan_id,
        workout_plan_id=workout_plan.workout_plan_id,
        bmi_value=21.4,
    )
    db.session.add(recommendation)
    db.session.commit()

    response = client.get("/api/v1/recommendations/latest", headers=auth_headers(token))
    assert response.status_code == 200
    body = response.get_json()["recommendation"]

    assert body["bmi_value"] == "21.4"
    assert body["body_type"]["name"] == "Normal"
    assert body["meal_plan"]["plan_code"] == "MP-TEST"
    assert body["meal_plan"]["calories"] == 1900
    assert body["workout_plan"]["plan_code"] == "WP-TEST"
    assert body["workout_plan"]["calories_burned"] == 400


def test_latest_recommendation_returns_most_recent_of_several(client, db):
    token = register_and_get_token(client)
    user = User.query.filter_by(username="dash_user").first()

    body_type = BodyTypeCategory(name="Normal", description="d")
    bmi_category = BMICategory(category_name="Normal weight", min_bmi=18.5, max_bmi=25.0)
    age_group = AgeGroup(name="Adult", min_age=20, max_age=59)
    db.session.add_all([body_type, bmi_category, age_group])
    db.session.commit()

    meal_plan = MealPlan(
        plan_code="MP-1",
        body_type_id=body_type.body_type_id,
        bmi_category_id=bmi_category.bmi_category_id,
        age_group_id=age_group.age_group_id,
        gender="female",
        breakfast="x",
        lunch="x",
        dinner="x",
        calories=1900,
        protein_g=75,
        carbs_g=240,
        fat_g=55,
    )
    workout_plan = WorkoutPlan(
        plan_code="WP-1",
        body_type_id=body_type.body_type_id,
        bmi_category_id=bmi_category.bmi_category_id,
        age_group_id=age_group.age_group_id,
        gender="female",
        warm_up="x",
        cardio="x",
        strength_training="x",
        stretching="x",
        cool_down="x",
        duration_minutes=55,
        calories_burned=400,
    )
    db.session.add_all([meal_plan, workout_plan])
    db.session.commit()

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
        meal_plan_id=meal_plan.meal_plan_id,
        workout_plan_id=workout_plan.workout_plan_id,
        bmi_value=21.0,
    )
    db.session.add(older)
    db.session.commit()

    newer = UserRecommendation(
        user_id=user.user_id,
        analysis_id=newer_analysis.analysis_id,
        meal_plan_id=meal_plan.meal_plan_id,
        workout_plan_id=workout_plan.workout_plan_id,
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
