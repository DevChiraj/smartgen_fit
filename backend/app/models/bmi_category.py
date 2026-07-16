"""BMI category reference ranges (Underweight / Normal / Overweight / Obese)."""

from app.extensions import db


class BMICategory(db.Model):
    __tablename__ = "bmi_categories"

    bmi_category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), unique=True, nullable=False)
    min_bmi = db.Column(db.Numeric(4, 1), nullable=False)
    max_bmi = db.Column(db.Numeric(4, 1), nullable=False)

    meal_plans = db.relationship("MealPlan", back_populates="bmi_category")
    workout_plans = db.relationship("WorkoutPlan", back_populates="bmi_category")

    def __repr__(self) -> str:
        return f"<BMICategory {self.category_name}>"
