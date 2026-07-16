"""Age group reference bands (Teenager / Adult / Senior)."""

from app.extensions import db


class AgeGroup(db.Model):
    __tablename__ = "age_groups"

    age_group_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    min_age = db.Column(db.Integer, nullable=False)
    max_age = db.Column(db.Integer, nullable=False)

    meal_plans = db.relationship("MealPlan", back_populates="age_group")
    workout_plans = db.relationship("WorkoutPlan", back_populates="age_group")

    def __repr__(self) -> str:
        return f"<AgeGroup {self.name}>"
