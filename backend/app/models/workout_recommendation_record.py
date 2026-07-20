"""Per-person workout record from the workout dataset (Module 11).

person_id is a real foreign key into meal_recommendation_records -
verified 1:1, no orphans on either side, before this constraint was
added (see documentation/module_reports/module11.md).
"""

from app.extensions import db


class WorkoutRecommendationRecord(db.Model):
    __tablename__ = "workout_recommendation_records"

    record_id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(
        db.String(20),
        db.ForeignKey("meal_recommendation_records.person_id"),
        unique=True,
        nullable=False,
        index=True,
    )

    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    fitness_level = db.Column(db.String(20), nullable=False)

    workout_type = db.Column(db.String(50), nullable=False)
    workout_category = db.Column(db.String(50), nullable=False)
    intensity = db.Column(db.String(20), nullable=False)
    duration_min = db.Column(db.Integer, nullable=False)
    days_per_week = db.Column(db.Integer, nullable=False)
    calories_burned = db.Column(db.Integer, nullable=False)
    target_muscle = db.Column(db.String(50), nullable=False)
    equipment = db.Column(db.String(50), nullable=True)
    indoor_outdoor = db.Column(db.String(20), nullable=False)
    goal = db.Column(db.String(50), nullable=False)
    warmup_min = db.Column(db.Integer, nullable=False)
    cooldown_min = db.Column(db.Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<WorkoutRecommendationRecord {self.person_id}>"
