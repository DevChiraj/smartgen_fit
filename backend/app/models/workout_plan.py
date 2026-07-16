"""Predefined workout plans, looked up by (body type, BMI category, age group, gender)."""

from app.extensions import db


class WorkoutPlan(db.Model):
    __tablename__ = "workout_plans"
    __table_args__ = (
        db.UniqueConstraint(
            "body_type_id",
            "bmi_category_id",
            "age_group_id",
            "gender",
            name="uq_workout_plan_lookup",
        ),
    )

    workout_plan_id = db.Column(db.Integer, primary_key=True)
    plan_code = db.Column(db.String(50), unique=True, nullable=False)
    body_type_id = db.Column(
        db.Integer, db.ForeignKey("body_type_categories.body_type_id"), nullable=False
    )
    bmi_category_id = db.Column(
        db.Integer, db.ForeignKey("bmi_categories.bmi_category_id"), nullable=False
    )
    age_group_id = db.Column(db.Integer, db.ForeignKey("age_groups.age_group_id"), nullable=False)
    gender = db.Column(db.String(20), nullable=False)

    warm_up = db.Column(db.Text, nullable=False)
    cardio = db.Column(db.Text, nullable=False)
    strength_training = db.Column(db.Text, nullable=False)
    stretching = db.Column(db.Text, nullable=False)
    cool_down = db.Column(db.Text, nullable=False)

    duration_minutes = db.Column(db.Integer, nullable=False)
    repetitions = db.Column(db.String(100), nullable=True)
    weekly_schedule = db.Column(db.String(255), nullable=True)
    calories_burned = db.Column(db.Integer, nullable=True)

    body_type = db.relationship("BodyTypeCategory", back_populates="workout_plans")
    bmi_category = db.relationship("BMICategory", back_populates="workout_plans")
    age_group = db.relationship("AgeGroup", back_populates="workout_plans")
    recommendations = db.relationship("UserRecommendation", back_populates="workout_plan")

    def __repr__(self) -> str:
        return f"<WorkoutPlan {self.plan_code}>"
