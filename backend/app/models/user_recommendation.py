"""Links a user's image analysis to the meal/workout plans looked up for it."""

from app.extensions import db
from app.models.mixins import utcnow


class UserRecommendation(db.Model):
    __tablename__ = "user_recommendations"

    recommendation_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    analysis_id = db.Column(
        db.Integer, db.ForeignKey("image_analysis_records.analysis_id"), nullable=False
    )
    meal_plan_id = db.Column(db.Integer, db.ForeignKey("meal_plans.meal_plan_id"), nullable=False)
    workout_plan_id = db.Column(
        db.Integer, db.ForeignKey("workout_plans.workout_plan_id"), nullable=False
    )
    bmi_value = db.Column(db.Numeric(4, 1), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    user = db.relationship("User", back_populates="recommendations")
    analysis = db.relationship("ImageAnalysisRecord", back_populates="recommendations")
    meal_plan = db.relationship("MealPlan", back_populates="recommendations")
    workout_plan = db.relationship("WorkoutPlan", back_populates="recommendations")

    def __repr__(self) -> str:
        return f"<UserRecommendation {self.recommendation_id}>"
