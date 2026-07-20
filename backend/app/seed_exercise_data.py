"""Parses the Module 13 Kaggle exercise dataset into rows for `exercises`.
Kept separate from seed.py's small hand-written reference tables, same
reasoning as seed_food_data.py (Module 12): real sourced data with
actual parsing, not a short literal list.

Source: Kaggle `prajwaldongre/best-50-exercise-for-your-body` (CC0-1.0).
This is a standalone exercise reference library for the public Workouts
page - unrelated to the Module 11 KNN recommendation pipeline
(workout_recommendation_records) or the legacy Module 2 workout_plans
template table.
"""

from pathlib import Path

import pandas as pd

from app.config import PROJECT_ROOT

EXERCISE_CSV = Path(PROJECT_ROOT) / "datasets" / "workouts" / "Top50ExercisesForYourBody.csv"


def load_exercise_records(path=EXERCISE_CSV) -> list[dict]:
    df = pd.read_excel(path) if str(path).endswith(".xlsx") else pd.read_csv(path)
    records = []
    for row in df.to_dict(orient="records"):
        equipment = row["Equipment Needed"]
        records.append(
            dict(
                exercise_name=str(row["Name of Exercise"]).strip(),
                target_muscle=str(row["Target Muscle Group"]).strip(),
                difficulty=str(row["Difficulty Level"]).strip(),
                equipment=None if pd.isna(equipment) else str(equipment).strip(),
                sets=int(row["Sets"]),
                reps=int(row["Reps"]),
                calories_per_30min=int(row["Burns Calories (per 30 min)"]),
                benefit=str(row["Benefit"]).strip(),
            )
        )
    return records
