"""Per-person meal record from the Sri Lankan meal dataset (Module 11).

One row per synthetic person (Person_ID), used as the candidate pool
the KNN recommender matches a user against - not a small set of
templates like the original meal_plans table. Age/Gender/BMI here are
the record's own values as they appear in the source dataset, kept
denormalized (also present in WorkoutRecommendationRecord) rather than
joined, since the two datasets are independently loaded from separate
files sharing the same Person_ID.
"""

from app.extensions import db


class MealRecommendationRecord(db.Model):
    __tablename__ = "meal_recommendation_records"

    record_id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.String(20), unique=True, nullable=False, index=True)

    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    height_cm = db.Column(db.Numeric(5, 2), nullable=False)
    weight_kg = db.Column(db.Numeric(5, 2), nullable=False)
    bmi = db.Column(db.Numeric(4, 1), nullable=False)
    bmi_category = db.Column(db.String(20), nullable=False)

    breakfast = db.Column(db.String(255), nullable=False)
    morning_snack = db.Column(db.String(255), nullable=False)
    lunch = db.Column(db.String(255), nullable=False)
    evening_snack = db.Column(db.String(255), nullable=False)
    dinner = db.Column(db.String(255), nullable=False)
    daily_calories = db.Column(db.Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<MealRecommendationRecord {self.person_id}>"
