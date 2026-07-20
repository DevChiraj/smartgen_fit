from datetime import datetime, timezone
from io import BytesIO

from PIL import Image

from app.extensions import db
from app.models import AIModelFile, BodyTypeCategory, MealRecommendationRecord
from app.models.workout_recommendation_record import WorkoutRecommendationRecord


def make_test_image_bytes():
    buffer = BytesIO()
    Image.new("RGB", (30, 30), color="blue").save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def register_and_get_token(client, username="analysis_user"):
    payload = {
        "full_name": "Analysis User",
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


def seed_active_model(fake_accuracy=0.6):
    model_file = AIModelFile(
        version="v_test",
        file_path="ai_model/saved_models/v_test.keras",
        accuracy=fake_accuracy,
        trained_date=datetime.now(timezone.utc),
        is_active=True,
    )
    db.session.add(model_file)
    db.session.commit()
    return model_file


def seed_body_types():
    for name in ("Thin", "Normal", "Overweight"):
        db.session.add(BodyTypeCategory(name=name, description=f"{name} body type"))
    db.session.commit()


def seed_recommendation_records(person_id="P001"):
    db.session.add(
        MealRecommendationRecord(
            person_id=person_id,
            age=30,
            gender="Female",
            height_cm=165,
            weight_kg=60,
            bmi=22.0,
            bmi_category="Normal",
            breakfast="x",
            morning_snack="x",
            lunch="x",
            evening_snack="x",
            dinner="x",
            daily_calories=2000,
        )
    )
    db.session.add(
        WorkoutRecommendationRecord(
            person_id=person_id,
            age=30,
            gender="Female",
            fitness_level="Intermediate",
            workout_type="Yoga",
            workout_category="Flexibility",
            intensity="Low",
            duration_min=45,
            days_per_week=5,
            calories_burned=180,
            target_muscle="Core",
            equipment="Mat",
            indoor_outdoor="Indoor",
            goal="Maintenance",
            warmup_min=10,
            cooldown_min=5,
        )
    )
    db.session.commit()


def mock_recommendation_match(monkeypatch, person_id="P001"):
    monkeypatch.setattr(
        "app.services.recommendation_service.ml_recommendation.find_matching_person",
        lambda label, age, gender: person_id,
    )


def test_analyze_requires_auth(client, db):
    response = client.post(
        "/api/v1/image-analysis",
        data={"image": (make_test_image_bytes(), "photo.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 401


def test_analyze_returns_503_when_no_active_model(client, db):
    token = register_and_get_token(client)
    response = client.post(
        "/api/v1/image-analysis",
        headers=auth_headers(token),
        data={"image": (make_test_image_bytes(), "photo.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 503
    assert response.get_json()["error"] == "NoActiveModelError"


def test_analyze_rejects_non_image(client, db):
    seed_active_model()
    token = register_and_get_token(client)

    response = client.post(
        "/api/v1/image-analysis",
        headers=auth_headers(token),
        data={"image": (BytesIO(b"not an image"), "fake.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "ValidationFailedError"


def test_analyze_success_with_mocked_inference(client, db, monkeypatch):
    seed_active_model()
    seed_body_types()
    seed_recommendation_records()
    token = register_and_get_token(client)

    monkeypatch.setattr(
        "app.services.image_analysis_service.classify_body_image",
        lambda image_path, model_path: ("normal", 0.87),
    )
    mock_recommendation_match(monkeypatch)

    response = client.post(
        "/api/v1/image-analysis",
        headers=auth_headers(token),
        data={"image": (make_test_image_bytes(), "photo.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    body = response.get_json()["analysis"]
    assert body["predicted_body_type"]["name"] == "Normal"
    assert body["confidence_score"] == "0.8700"
    assert body["image_path"].startswith("/api/v1/image-analysis/uploads/")

    served = client.get(body["image_path"])
    assert served.status_code == 200
    assert served.content_type == "image/png"


def test_history_requires_auth(client, db):
    response = client.get("/api/v1/image-analysis/history")
    assert response.status_code == 401


def test_history_returns_only_the_current_users_records(client, db, monkeypatch):
    seed_active_model()
    seed_body_types()
    seed_recommendation_records()
    monkeypatch.setattr(
        "app.services.image_analysis_service.classify_body_image",
        lambda image_path, model_path: ("thin", 0.75),
    )
    mock_recommendation_match(monkeypatch)

    token_a = register_and_get_token(client, username="user_a")
    client.post(
        "/api/v1/image-analysis",
        headers=auth_headers(token_a),
        data={"image": (make_test_image_bytes(), "photo.png")},
        content_type="multipart/form-data",
    )

    token_b = register_and_get_token(client, username="user_b")
    response = client.get("/api/v1/image-analysis/history", headers=auth_headers(token_b))
    assert response.status_code == 200
    assert response.get_json()["history"] == []

    response = client.get("/api/v1/image-analysis/history", headers=auth_headers(token_a))
    assert response.status_code == 200
    history = response.get_json()["history"]
    assert len(history) == 1
    assert history[0]["predicted_body_type"]["name"] == "Thin"


def test_analyze_returns_error_when_predicted_label_has_no_matching_body_type(
    client, db, monkeypatch
):
    seed_active_model()
    # deliberately not seeding body types
    token = register_and_get_token(client)
    monkeypatch.setattr(
        "app.services.image_analysis_service.classify_body_image",
        lambda image_path, model_path: ("normal", 0.9),
    )

    response = client.post(
        "/api/v1/image-analysis",
        headers=auth_headers(token),
        data={"image": (make_test_image_bytes(), "photo.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 500


def test_analyze_creates_a_matched_recommendation(client, db, monkeypatch):
    from app.models import UserRecommendation

    seed_active_model()
    seed_body_types()
    seed_recommendation_records(person_id="P042")
    token = register_and_get_token(client)

    monkeypatch.setattr(
        "app.services.image_analysis_service.classify_body_image",
        lambda image_path, model_path: ("normal", 0.87),
    )
    mock_recommendation_match(monkeypatch, person_id="P042")

    response = client.post(
        "/api/v1/image-analysis",
        headers=auth_headers(token),
        data={"image": (make_test_image_bytes(), "photo.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    analysis_id = response.get_json()["analysis"]["analysis_id"]

    recommendation = UserRecommendation.query.filter_by(analysis_id=analysis_id).first()
    assert recommendation is not None
    assert recommendation.matched_person_id == "P042"


def test_analyze_returns_503_and_creates_no_orphaned_analysis_when_recommender_missing(
    client, db, monkeypatch
):
    from app.models import ImageAnalysisRecord

    seed_active_model()
    seed_body_types()
    # deliberately not seeding meal/workout recommendation records
    token = register_and_get_token(client)

    monkeypatch.setattr(
        "app.services.image_analysis_service.classify_body_image",
        lambda image_path, model_path: ("normal", 0.87),
    )

    def raise_not_found(label, age, gender):
        raise FileNotFoundError()

    monkeypatch.setattr(
        "app.services.recommendation_service.ml_recommendation.find_matching_person",
        raise_not_found,
    )

    response = client.post(
        "/api/v1/image-analysis",
        headers=auth_headers(token),
        data={"image": (make_test_image_bytes(), "photo.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 503
    assert response.get_json()["error"] == "NoRecommenderModelError"
    assert ImageAnalysisRecord.query.count() == 0
