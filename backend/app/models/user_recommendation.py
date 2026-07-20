"""Links a user's image analysis to their matched meal/workout records.

Module 11 replaced the original composite-key rule-based lookup with a
KNN similarity match against meal_recommendation_records /
workout_recommendation_records (see CLAUDE.md rule 2 and
documentation/module_reports/module11.md for the full rationale).
meal_plan_id/workout_plan_id are kept nullable for backward
compatibility with the original template-based design; new rows use
matched_person_id instead.
"""

from app.extensions import db
from app.models.mixins import utcnow


class UserRecommendation(db.Model):
    __tablename__ = "user_recommendations"

    recommendation_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    analysis_id = db.Column(
        db.Integer, db.ForeignKey("image_analysis_records.analysis_id"), nullable=False
    )
    meal_plan_id = db.Column(db.Integer, db.ForeignKey("meal_plans.meal_plan_id"), nullable=True)
    workout_plan_id = db.Column(
        db.Integer, db.ForeignKey("workout_plans.workout_plan_id"), nullable=True
    )
    matched_person_id = db.Column(
        db.String(20), db.ForeignKey("meal_recommendation_records.person_id"), nullable=True
    )
    bmi_value = db.Column(db.Numeric(4, 1), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    user = db.relationship("User", back_populates="recommendations")
    analysis = db.relationship("ImageAnalysisRecord", back_populates="recommendations")
    meal_plan = db.relationship("MealPlan", back_populates="recommendations")
    workout_plan = db.relationship("WorkoutPlan", back_populates="recommendations")
    matched_meal_record = db.relationship("MealRecommendationRecord")

    def __repr__(self) -> str:
        return f"<UserRecommendation {self.recommendation_id}>"
