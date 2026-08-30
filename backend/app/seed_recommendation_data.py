"""CLI command: loads the Module 11 meal/workout Excel datasets into
meal_recommendation_records / workout_recommendation_records.

    flask seed-recommendations

Idempotent - re-running replaces rows by Person_ID rather than duplicating
them, same pattern as app/seed.py.
"""

from pathlib import Path

import click
import pandas as pd

from app.config import PROJECT_ROOT
from app.repositories import meal_recommendation_repository, workout_recommendation_repository

MEAL_XLSX = (
    Path(PROJECT_ROOT) / "datasets" / "recommendations" / "Sri_Lankan_Meal_Dataset_NEW.xlsx"
)
WORKOUT_XLSX = (
    Path(PROJECT_ROOT) / "datasets" / "recommendations" / "Workout_Dataset_Matched_Advanced.xlsx"
)


def _load_meal_records(path) -> list[dict]:
    df = pd.read_excel(path)
    records = []
    for row in df.itertuples(index=False):
        records.append(
            dict(
                person_id=str(row.Person_ID),
                age=int(row.Age),
                gender=str(row.Gender),
                height_cm=float(row.Height_cm),
                weight_kg=float(row.Weight_kg),
                bmi=float(row.BMI),
                bmi_category=str(row.BMI_Category),
                breakfast=str(row.Breakfast),
                morning_snack=str(row.Morning_Snack),
                lunch=str(row.Lunch),
                evening_snack=str(row.Evening_Snack),
                dinner=str(row.Dinner),
                daily_calories=int(row.Daily_Calories),
            )
        )
    return records


def _load_workout_records(path) -> list[dict]:
    df = pd.read_excel(path)
    records = []
    for row in df.itertuples(index=False):
        equipment = row.Equipment
        records.append(
            dict(
                person_id=str(row.Person_ID),
                age=int(row.Age),
                gender=str(row.Gender),
                fitness_level=str(row.Fitness_Level),
                workout_type=str(row.Workout_Type),
                workout_category=str(row.Workout_Category),
                intensity=str(row.Intensity),
                duration_min=int(row.Duration_Min),
                days_per_week=int(row.Days_Per_Week),
                calories_burned=int(row.Calories_Burned),
                target_muscle=str(row.Target_Muscle),
                equipment=None if pd.isna(equipment) else str(equipment),
                indoor_outdoor=str(row.Indoor_Outdoor),
                goal=str(row.Goal),
                warmup_min=int(row.Warmup_Min),
                cooldown_min=int(row.Cooldown_Min),
            )
        )
    return records


def seed_recommendation_data(meal_path=MEAL_XLSX, workout_path=WORKOUT_XLSX) -> tuple[int, int]:
    """Load both datasets, meal first (workout rows FK into it by person_id)."""
    meal_records = _load_meal_records(meal_path)
    meal_recommendation_repository.bulk_upsert(meal_records)

    workout_records = _load_workout_records(workout_path)
    workout_recommendation_repository.bulk_upsert(workout_records)

    return len(meal_records), len(workout_records)


def register_seed_recommendation_command(app):
    @app.cli.command("seed-recommendations")
    @click.option("--meal-path", default=str(MEAL_XLSX))
    @click.option("--workout-path", default=str(WORKOUT_XLSX))
    def seed_recommendations_cli(meal_path, workout_path):
        meal_count, workout_count = seed_recommendation_data(meal_path, workout_path)
        click.echo(f"Loaded {meal_count} meal records and {workout_count} workout records.")
