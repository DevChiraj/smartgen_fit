"""Predefined meal plans, looked up by (body type, BMI category, age group, gender)."""

from app.extensions import db


class MealPlan(db.Model):
    __tablename__ = "meal_plans"
    __table_args__ = (
        db.UniqueConstraint(
            "body_type_id",
            "bmi_category_id",
            "age_group_id",
            "gender",
            name="uq_meal_plan_lookup",
        ),
    )

    meal_plan_id = db.Column(db.Integer, primary_key=True)
    plan_code = db.Column(db.String(50), unique=True, nullable=False)
    body_type_id = db.Column(
        db.Integer, db.ForeignKey("body_type_categories.body_type_id"), nullable=False
    )
    bmi_category_id = db.Column(
        db.Integer, db.ForeignKey("bmi_categories.bmi_category_id"), nullable=False
    )
    age_group_id = db.Column(db.Integer, db.ForeignKey("age_groups.age_group_id"), nullable=False)
    gender = db.Column(db.String(20), nullable=False)

    breakfast = db.Column(db.Text, nullable=False)
    lunch = db.Column(db.Text, nullable=False)
    dinner = db.Column(db.Text, nullable=False)
    snacks = db.Column(db.Text, nullable=True)

    calories = db.Column(db.Integer, nullable=False)
    protein_g = db.Column(db.Numeric(6, 2), nullable=False)
    carbs_g = db.Column(db.Numeric(6, 2), nullable=False)
    fat_g = db.Column(db.Numeric(6, 2), nullable=False)
    fiber_g = db.Column(db.Numeric(6, 2), nullable=True)
    vitamins = db.Column(db.String(255), nullable=True)
    minerals = db.Column(db.String(255), nullable=True)
    daily_water_ml = db.Column(db.Integer, nullable=True)

    body_type = db.relationship("BodyTypeCategory", back_populates="meal_plans")
    bmi_category = db.relationship("BMICategory", back_populates="meal_plans")
    age_group = db.relationship("AgeGroup", back_populates="meal_plans")
    recommendations = db.relationship("UserRecommendation", back_populates="meal_plan")

    def __repr__(self) -> str:
        return f"<MealPlan {self.plan_code}>"
