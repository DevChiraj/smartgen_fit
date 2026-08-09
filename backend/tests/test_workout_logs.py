from app.extensions import db
from app.models import Exercise


def register_and_get_token(client, username="tracker_user"):
    payload = {
        "full_name": "Tracker User",
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


def seed_exercise(**overrides):
    defaults = dict(
        exercise_name="Push Up",
        target_muscle="Chest",
        difficulty="Beginner",
        equipment=None,
        sets=3,
        reps=15,
        calories_per_30min=180,
        benefit="Builds upper body strength.",
    )
    defaults.update(overrides)
    exercise = Exercise(**defaults)
    db.session.add(exercise)
    db.session.commit()
    return exercise


def test_log_workout_requires_auth(client, db):
    response = client.post("/api/v1/workout-logs", json={"exercise_id": 1, "duration_minutes": 30})
    assert response.status_code == 401


def test_history_requires_auth(client, db):
    response = client.get("/api/v1/workout-logs")
    assert response.status_code == 401


def test_log_workout_success_derives_calories_from_exercise_rate(client, db):
    exercise = seed_exercise()
    token = register_and_get_token(client)

    response = client.post(
        "/api/v1/workout-logs",
        headers=auth_headers(token),
        json={"exercise_id": exercise.exercise_id, "duration_minutes": 15},
    )
    assert response.status_code == 201
    log = response.get_json()["log"]
    assert log["duration_minutes"] == 15
    assert log["calories_burned"] == 90  # 180 * 15 / 30
    assert log["exercise"]["exercise_name"] == "Push Up"
    assert log["log_date"] is not None


def test_log_workout_accepts_explicit_calories_and_date_and_notes(client, db):
    exercise = seed_exercise()
    token = register_and_get_token(client)

    response = client.post(
        "/api/v1/workout-logs",
        headers=auth_headers(token),
        json={
            "exercise_id": exercise.exercise_id,
            "duration_minutes": 45,
            "calories_burned": 500,
            "log_date": "2026-08-01",
            "notes": "Felt great today.",
        },
    )
    assert response.status_code == 201
    log = response.get_json()["log"]
    assert log["calories_burned"] == 500
    assert log["log_date"] == "2026-08-01"
    assert log["notes"] == "Felt great today."


def test_log_workout_rejects_unknown_exercise(client, db):
    token = register_and_get_token(client)
    response = client.post(
        "/api/v1/workout-logs",
        headers=auth_headers(token),
        json={"exercise_id": 999, "duration_minutes": 30},
    )
    assert response.status_code == 404


def test_log_workout_rejects_missing_required_fields(client, db):
    exercise = seed_exercise()
    token = register_and_get_token(client)
    response = client.post(
        "/api/v1/workout-logs",
        headers=auth_headers(token),
        json={"exercise_id": exercise.exercise_id},
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "ValidationError"


def test_log_workout_rejects_out_of_range_duration(client, db):
    exercise = seed_exercise()
    token = register_and_get_token(client)
    response = client.post(
        "/api/v1/workout-logs",
        headers=auth_headers(token),
        json={"exercise_id": exercise.exercise_id, "duration_minutes": 0},
    )
    assert response.status_code == 400


def test_history_returns_only_the_current_users_logs_newest_first(client, db):
    exercise = seed_exercise()
    token_a = register_and_get_token(client, username="user_a")
    token_b = register_and_get_token(client, username="user_b")

    client.post(
        "/api/v1/workout-logs",
        headers=auth_headers(token_a),
        json={
            "exercise_id": exercise.exercise_id,
            "duration_minutes": 20,
            "log_date": "2026-08-01",
        },
    )
    client.post(
        "/api/v1/workout-logs",
        headers=auth_headers(token_a),
        json={
            "exercise_id": exercise.exercise_id,
            "duration_minutes": 20,
            "log_date": "2026-08-05",
        },
    )

    response = client.get("/api/v1/workout-logs", headers=auth_headers(token_b))
    assert response.status_code == 200
    assert response.get_json()["history"] == []

    response = client.get("/api/v1/workout-logs", headers=auth_headers(token_a))
    assert response.status_code == 200
    history = response.get_json()["history"]
    assert len(history) == 2
    assert history[0]["log_date"] == "2026-08-05"
    assert history[1]["log_date"] == "2026-08-01"
