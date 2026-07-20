import pandas as pd

from app.repositories import meal_recommendation_repository, workout_recommendation_repository
from app.seed_recommendation_data import (
    _load_meal_records,
    _load_workout_records,
    seed_recommendation_data,
)


def _make_meal_xlsx(tmp_path):
    df = pd.DataFrame(
        [
            {
                "Person_ID": "P001",
                "Age": 28,
                "Gender": "Female",
                "Height_cm": 165,
                "Weight_kg": 58,
                "BMI": 21.3,
                "BMI_Category": "Normal",
                "Breakfast": "String hoppers",
                "Morning_Snack": "Papaya",
                "Lunch": "Rice and curry",
                "Evening_Snack": "Nuts",
                "Dinner": "Soup",
                "Daily_Calories": 1900,
            }
        ]
    )
    path = tmp_path / "meal.xlsx"
    df.to_excel(path, index=False)
    return path


def _make_workout_xlsx(tmp_path):
    df = pd.DataFrame(
        [
            {
                "Person_ID": "P001",
                "Age": 28,
                "Gender": "Female",
                "Fitness_Level": "Intermediate",
                "Workout_Type": "Cycling",
                "Workout_Category": "Cardio",
                "Intensity": "Moderate",
                "Duration_Min": 40,
                "Days_Per_Week": 4,
                "Calories_Burned": 400,
                "Target_Muscle": "Full body",
                "Equipment": "Bicycle",
                "Indoor_Outdoor": "Outdoor",
                "Goal": "Weight maintenance",
                "Warmup_Min": 8,
                "Cooldown_Min": 5,
            },
            {
                "Person_ID": "P002",
                "Age": 35,
                "Gender": "Male",
                "Fitness_Level": "Beginner",
                "Workout_Type": "Bodyweight circuit",
                "Workout_Category": "Strength",
                "Intensity": "Low",
                "Duration_Min": 25,
                "Days_Per_Week": 3,
                "Calories_Burned": 180,
                "Target_Muscle": "Full body",
                "Equipment": None,
                "Indoor_Outdoor": "Indoor",
                "Goal": "General fitness",
                "Warmup_Min": 5,
                "Cooldown_Min": 5,
            },
        ]
    )
    path = tmp_path / "workout.xlsx"
    df.to_excel(path, index=False)
    return path


def test_load_meal_records_parses_real_column_names(tmp_path):
    records = _load_meal_records(_make_meal_xlsx(tmp_path))

    assert len(records) == 1
    record = records[0]
    assert record["person_id"] == "P001"
    assert record["age"] == 28
    assert record["bmi"] == 21.3
    assert record["bmi_category"] == "Normal"
    assert record["daily_calories"] == 1900


def test_load_workout_records_converts_missing_equipment_to_none(tmp_path):
    records = _load_workout_records(_make_workout_xlsx(tmp_path))

    with_equipment = next(r for r in records if r["person_id"] == "P001")
    bodyweight = next(r for r in records if r["person_id"] == "P002")

    assert with_equipment["equipment"] == "Bicycle"
    assert bodyweight["equipment"] is None


def test_seed_recommendation_data_loads_both_datasets(app, db, tmp_path):
    meal_path = _make_meal_xlsx(tmp_path)
    workout_path = _make_workout_xlsx(tmp_path)

    meal_count, workout_count = seed_recommendation_data(meal_path, workout_path)

    assert meal_count == 1
    assert workout_count == 2
    assert meal_recommendation_repository.count() == 1
    assert workout_recommendation_repository.count() == 2
