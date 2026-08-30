from datetime import date, timedelta

from app.extensions import db
from app.models import SriLankanFood, User


def register_and_get_token(client, username="alert_user"):
    payload = {
        "full_name": "Alert User",
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


def get_user(username):
    return User.query.filter_by(username=username).first()


def set_created_at(username, days_ago):
    user = get_user(username)
    user.created_at = user.created_at - timedelta(days=days_ago)
    db.session.commit()


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


def log_workout(client, token, exercise_id, log_date):
    return client.post(
        "/api/v1/workout-logs",
        headers=auth_headers(token),
        json={"exercise_id": exercise_id, "duration_minutes": 20, "log_date": log_date},
    )


def log_meal(client, token, food_id, meal_type, log_date, quantity_servings=1):
    return client.post(
        "/api/v1/meal-logs",
        headers=auth_headers(token),
        json={
            "food_id": food_id,
            "meal_type": meal_type,
            "log_date": log_date,
            "quantity_servings": quantity_servings,
        },
    )


def test_notifications_requires_auth(client, db):
    response = client.get("/api/v1/notifications")
    assert response.status_code == 401


def test_brand_new_user_has_no_notifications(client, db):
    token = register_and_get_token(client)
    response = client.get("/api/v1/notifications", headers=auth_headers(token))
    assert response.status_code == 200
    assert response.get_json()["notifications"] == []


def test_exercise_inactivity_alert_fires_based_on_account_age_when_never_logged(client, db):
    token = register_and_get_token(client)
    set_created_at("alert_user", days_ago=5)

    response = client.get("/api/v1/notifications", headers=auth_headers(token))
    alerts = [n for n in response.get_json()["notifications"] if n["type"] == "exercise_inactivity"]
    assert len(alerts) == 1
    assert "5 days" in alerts[0]["message"]
    assert alerts[0]["severity"] == "warning"


def test_exercise_inactivity_alert_fires_based_on_most_recent_log(client, db):
    from tests.test_workout_logs import seed_exercise

    exercise = seed_exercise()
    token = register_and_get_token(client)
    set_created_at("alert_user", days_ago=30)
    old_date = (date.today() - timedelta(days=4)).isoformat()
    log_workout(client, token, exercise.exercise_id, old_date)

    response = client.get("/api/v1/notifications", headers=auth_headers(token))
    alerts = [n for n in response.get_json()["notifications"] if n["type"] == "exercise_inactivity"]
    assert len(alerts) == 1
    assert "4 days" in alerts[0]["message"]


def test_no_exercise_inactivity_alert_when_recently_active(client, db):
    from tests.test_workout_logs import seed_exercise

    exercise = seed_exercise()
    token = register_and_get_token(client)
    set_created_at("alert_user", days_ago=30)
    log_workout(client, token, exercise.exercise_id, date.today().isoformat())

    response = client.get("/api/v1/notifications", headers=auth_headers(token))
    alerts = [n for n in response.get_json()["notifications"] if n["type"] == "exercise_inactivity"]
    assert alerts == []


def test_no_skipped_meal_alerts_for_a_user_who_has_never_used_the_diary(client, db):
    token = register_and_get_token(client)
    set_created_at("alert_user", days_ago=0)

    response = client.get("/api/v1/notifications", headers=auth_headers(token))
    alerts = [n for n in response.get_json()["notifications"] if n["type"] == "skipped_meal"]
    assert alerts == []


def test_skipped_meal_alerts_fire_for_missing_core_meals_yesterday(client, db):
    food = seed_food()
    token = register_and_get_token(client)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    # Only breakfast logged yesterday - lunch and dinner skipped.
    log_meal(client, token, food.food_id, "breakfast", yesterday)

    response = client.get("/api/v1/notifications", headers=auth_headers(token))
    alerts = [n for n in response.get_json()["notifications"] if n["type"] == "skipped_meal"]
    messages = {a["message"] for a in alerts}
    assert messages == {"You skipped lunch yesterday.", "You skipped dinner yesterday."}


def test_no_skipped_meal_alerts_when_all_core_meals_logged_yesterday(client, db):
    food = seed_food()
    token = register_and_get_token(client)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    for meal_type in ("breakfast", "lunch", "dinner"):
        log_meal(client, token, food.food_id, meal_type, yesterday)

    response = client.get("/api/v1/notifications", headers=auth_headers(token))
    alerts = [n for n in response.get_json()["notifications"] if n["type"] == "skipped_meal"]
    assert alerts == []


def test_no_low_protein_alert_without_a_weight_on_file(client, db):
    food = seed_food(protein_g=2)
    token = register_and_get_token(client)
    log_meal(client, token, food.food_id, "breakfast", date.today().isoformat())

    response = client.get("/api/v1/notifications", headers=auth_headers(token))
    alerts = [n for n in response.get_json()["notifications"] if n["type"] == "low_protein"]
    assert alerts == []


def test_no_low_protein_alert_when_nothing_logged_today(client, db):
    token = register_and_get_token(client)
    user = get_user("alert_user")
    user.weight_kg = 70
    db.session.commit()

    response = client.get("/api/v1/notifications", headers=auth_headers(token))
    alerts = [n for n in response.get_json()["notifications"] if n["type"] == "low_protein"]
    assert alerts == []


def test_low_protein_alert_fires_when_todays_intake_is_below_target(client, db):
    food = seed_food(protein_g=2)
    token = register_and_get_token(client)
    user = get_user("alert_user")
    user.weight_kg = 70  # target = 70 * 0.8 = 56g, 70% threshold = 39.2g
    db.session.commit()
    log_meal(client, token, food.food_id, "breakfast", date.today().isoformat())

    response = client.get("/api/v1/notifications", headers=auth_headers(token))
    alerts = [n for n in response.get_json()["notifications"] if n["type"] == "low_protein"]
    assert len(alerts) == 1
    assert "56g target" in alerts[0]["message"]


def test_no_low_protein_alert_when_todays_intake_meets_target(client, db):
    food = seed_food(protein_g=60)
    token = register_and_get_token(client)
    user = get_user("alert_user")
    user.weight_kg = 70
    db.session.commit()
    log_meal(client, token, food.food_id, "breakfast", date.today().isoformat())

    response = client.get("/api/v1/notifications", headers=auth_headers(token))
    alerts = [n for n in response.get_json()["notifications"] if n["type"] == "low_protein"]
    assert alerts == []
