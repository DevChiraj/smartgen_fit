"""Body type classification labels (Thin / Normal / Overweight)."""

from app.extensions import db


class BodyTypeCategory(db.Model):
    __tablename__ = "body_type_categories"

    body_type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    meal_plans = db.relationship("MealPlan", back_populates="body_type")
    workout_plans = db.relationship("WorkoutPlan", back_populates="body_type")
    image_analyses = db.relationship("ImageAnalysisRecord", back_populates="predicted_body_type")

    def __repr__(self) -> str:
        return f"<BodyTypeCategory {self.name}>"
