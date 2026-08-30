from app.extensions import db
from app.models import SriLankanFood


def register_and_get_token(client, username="diary_user"):
    payload = {
        "full_name": "Diary User",
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


def seed_food(**overrides):
    defaults = dict(
        food_name="Chicken Curry",
        category="Protein",
        serving_size="100g",
        calories=190,
        protein_g=24,
        carbs_g=4,
        fat_g=9,
    )
    defaults.update(overrides)
    food = SriLankanFood(**defaults)
    db.session.add(food)
    db.session.commit()
    return food


def test_log_meal_requires_auth(client, db):
    response = client.post("/api/v1/meal-logs", json={"food_id": 1, "meal_type": "lunch"})
    assert response.status_code == 401


def test_history_requires_auth(client, db):
    response = client.get("/api/v1/meal-logs")
    assert response.status_code == 401


def test_log_meal_success_derives_calories_and_protein_from_food(client, db):
    food = seed_food()
    token = register_and_get_token(client)

    response = client.post(
        "/api/v1/meal-logs",
        headers=auth_headers(token),
        json={"food_id": food.food_id, "meal_type": "lunch"},
    )
    assert response.status_code == 201
    log = response.get_json()["log"]
    assert log["quantity_servings"] == "1.00"
    assert log["calories"] == 190
    assert log["protein_g"] == "24.00"
    assert log["meal_type"] == "lunch"
    assert log["food"]["food_name"] == "Chicken Curry"
    assert log["log_date"] is not None


def test_log_meal_scales_by_quantity_servings(client, db):
    food = seed_food()
    token = register_and_get_token(client)

    response = client.post(
        "/api/v1/meal-logs",
        headers=auth_headers(token),
        json={"food_id": food.food_id, "meal_type": "dinner", "quantity_servings": 2},
    )
    assert response.status_code == 201
    log = response.get_json()["log"]
    assert log["calories"] == 380
    assert log["protein_g"] == "48.00"


def test_log_meal_accepts_explicit_date_and_notes(client, db):
    food = seed_food()
    token = register_and_get_token(client)

    response = client.post(
        "/api/v1/meal-logs",
        headers=auth_headers(token),
        json={
            "food_id": food.food_id,
            "meal_type": "breakfast",
            "log_date": "2026-08-01",
            "notes": "Extra hungry today.",
        },
    )
    assert response.status_code == 201
    log = response.get_json()["log"]
    assert log["log_date"] == "2026-08-01"
    assert log["notes"] == "Extra hungry today."


def test_log_meal_rejects_unknown_food(client, db):
    token = register_and_get_token(client)
    response = client.post(
        "/api/v1/meal-logs",
        headers=auth_headers(token),
        json={"food_id": 999, "meal_type": "lunch"},
    )
    assert response.status_code == 404


def test_log_meal_rejects_missing_required_fields(client, db):
    food = seed_food()
    token = register_and_get_token(client)
    response = client.post(
        "/api/v1/meal-logs",
        headers=auth_headers(token),
        json={"food_id": food.food_id},
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "ValidationError"


def test_log_meal_rejects_invalid_meal_type(client, db):
    food = seed_food()
    token = register_and_get_token(client)
    response = client.post(
        "/api/v1/meal-logs",
        headers=auth_headers(token),
        json={"food_id": food.food_id, "meal_type": "brunch"},
    )
    assert response.status_code == 400


def test_history_returns_only_the_current_users_logs_newest_first(client, db):
    food = seed_food()
    token_a = register_and_get_token(client, username="user_a")
    token_b = register_and_get_token(client, username="user_b")

    client.post(
        "/api/v1/meal-logs",
        headers=auth_headers(token_a),
        json={"food_id": food.food_id, "meal_type": "breakfast", "log_date": "2026-08-01"},
    )
    client.post(
        "/api/v1/meal-logs",
        headers=auth_headers(token_a),
        json={"food_id": food.food_id, "meal_type": "dinner", "log_date": "2026-08-05"},
    )

    response = client.get("/api/v1/meal-logs", headers=auth_headers(token_b))
    assert response.status_code == 200
    assert response.get_json()["history"] == []

    response = client.get("/api/v1/meal-logs", headers=auth_headers(token_a))
    assert response.status_code == 200
    history = response.get_json()["history"]
    assert len(history) == 2
    assert history[0]["log_date"] == "2026-08-05"
    assert history[1]["log_date"] == "2026-08-01"
