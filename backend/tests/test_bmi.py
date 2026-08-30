from app.extensions import db
from app.models import BMICategory

CATEGORIES = [
    ("Underweight", 0.0, 18.5),
    ("Normal weight", 18.5, 25.0),
    ("Overweight", 25.0, 30.0),
    ("Obese", 30.0, 60.0),
]


def seed_bmi_categories():
    for name, min_bmi, max_bmi in CATEGORIES:
        db.session.add(BMICategory(category_name=name, min_bmi=min_bmi, max_bmi=max_bmi))
    db.session.commit()


def test_calculate_bmi_normal_weight(client, db):
    seed_bmi_categories()
    response = client.post("/api/v1/bmi/calculate", json={"height_cm": 170, "weight_kg": 65})
    assert response.status_code == 200
    body = response.get_json()
    assert body["bmi"] == "22.5"
    assert body["category"]["category_name"] == "Normal weight"


def test_calculate_bmi_underweight(client, db):
    seed_bmi_categories()
    response = client.post("/api/v1/bmi/calculate", json={"height_cm": 175, "weight_kg": 45})
    assert response.status_code == 200
    assert response.get_json()["category"]["category_name"] == "Underweight"


def test_calculate_bmi_overweight(client, db):
    seed_bmi_categories()
    response = client.post("/api/v1/bmi/calculate", json={"height_cm": 170, "weight_kg": 80})
    assert response.status_code == 200
    assert response.get_json()["category"]["category_name"] == "Overweight"


def test_calculate_bmi_obese(client, db):
    seed_bmi_categories()
    response = client.post("/api/v1/bmi/calculate", json={"height_cm": 170, "weight_kg": 100})
    assert response.status_code == 200
    assert response.get_json()["category"]["category_name"] == "Obese"


def test_calculate_bmi_boundary_is_exclusive_upper(client, db):
    seed_bmi_categories()
    # Exactly 18.5 belongs to "Normal weight" (min inclusive), not "Underweight".
    response = client.post("/api/v1/bmi/calculate", json={"height_cm": 200, "weight_kg": 74})
    body = response.get_json()
    assert body["bmi"] == "18.5"
    assert body["category"]["category_name"] == "Normal weight"


def test_calculate_bmi_above_highest_range_falls_back_to_top_category(client, db):
    seed_bmi_categories()
    # A BMI above the highest defined max_bmi (60) should still classify as
    # the top category ("Obese") rather than returning no category.
    response = client.post("/api/v1/bmi/calculate", json={"height_cm": 150, "weight_kg": 200})
    assert response.status_code == 200
    assert response.get_json()["category"]["category_name"] == "Obese"


def test_calculate_bmi_missing_fields(client, db):
    response = client.post("/api/v1/bmi/calculate", json={"height_cm": 170})
    assert response.status_code == 400
    assert "weight_kg" in response.get_json()["message"]


def test_calculate_bmi_rejects_non_positive_weight(client, db):
    response = client.post("/api/v1/bmi/calculate", json={"height_cm": 170, "weight_kg": 0})
    assert response.status_code == 400


def test_calculate_bmi_rejects_unrealistic_height(client, db):
    response = client.post("/api/v1/bmi/calculate", json={"height_cm": 5, "weight_kg": 65})
    assert response.status_code == 400


def test_calculate_bmi_does_not_require_auth(client, db):
    seed_bmi_categories()
    response = client.post("/api/v1/bmi/calculate", json={"height_cm": 170, "weight_kg": 65})
    assert response.status_code == 200
