from app.extensions import db
from app.models import Exercise


def seed_exercises():
    exercises = [
        dict(
            exercise_name="Push-ups",
            target_muscle="Chest, Triceps, Shoulders",
            difficulty="Intermediate",
            equipment=None,
            sets=3,
            reps=15,
            calories_per_30min=200,
            benefit="Builds upper body strength",
        ),
        dict(
            exercise_name="Squats",
            target_muscle="Quadriceps, Hamstrings, Glutes",
            difficulty="Beginner",
            equipment=None,
            sets=4,
            reps=12,
            calories_per_30min=223,
            benefit="Strengthens lower body",
        ),
        dict(
            exercise_name="Dragon Flags",
            target_muscle="Full Core",
            difficulty="Advanced",
            equipment="Bench or Sturdy Surface",
            sets=3,
            reps=8,
            calories_per_30min=250,
            benefit="Advanced core exercise",
        ),
    ]
    for exercise in exercises:
        db.session.add(Exercise(**exercise))
    db.session.commit()


def test_list_exercises_does_not_require_auth(client, db):
    seed_exercises()
    response = client.get("/api/v1/exercises")
    assert response.status_code == 200
    assert len(response.get_json()["exercises"]) == 3


def test_list_exercises_filters_by_difficulty(client, db):
    seed_exercises()
    response = client.get("/api/v1/exercises?difficulty=Beginner")
    exercises = response.get_json()["exercises"]
    assert len(exercises) == 1
    assert exercises[0]["exercise_name"] == "Squats"


def test_list_exercises_difficulty_filter_is_case_insensitive(client, db):
    seed_exercises()
    response = client.get("/api/v1/exercises?difficulty=beginner")
    assert len(response.get_json()["exercises"]) == 1


def test_list_exercises_search_matches_partial_name(client, db):
    seed_exercises()
    response = client.get("/api/v1/exercises?q=push")
    exercises = response.get_json()["exercises"]
    assert len(exercises) == 1
    assert exercises[0]["exercise_name"] == "Push-ups"


def test_list_difficulties_returns_distinct_sorted_values(client, db):
    seed_exercises()
    response = client.get("/api/v1/exercises/difficulties")
    assert response.status_code == 200
    assert response.get_json()["difficulties"] == ["Advanced", "Beginner", "Intermediate"]


def test_get_exercise_returns_full_detail(client, db):
    seed_exercises()
    exercise = Exercise.query.filter_by(exercise_name="Squats").first()
    response = client.get(f"/api/v1/exercises/{exercise.exercise_id}")
    assert response.status_code == 200
    body = response.get_json()["exercise"]
    assert body["exercise_name"] == "Squats"
    assert body["sets"] == 4
    assert body["reps"] == 12


def test_get_exercise_returns_404_for_missing_id(client, db):
    response = client.get("/api/v1/exercises/999999")
    assert response.status_code == 404
    assert response.get_json()["error"] == "NotFoundError"


def test_get_exercise_returns_404_for_non_numeric_id(client, db):
    response = client.get("/api/v1/exercises/not-a-number")
    assert response.status_code == 404
