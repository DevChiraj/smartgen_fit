"""History of body-image classification runs (label + confidence only, no plan data)."""

from app.extensions import db
from app.models.mixins import utcnow


class ImageAnalysisRecord(db.Model):
    __tablename__ = "image_analysis_records"

    analysis_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    predicted_body_type_id = db.Column(
        db.Integer, db.ForeignKey("body_type_categories.body_type_id"), nullable=False
    )
    confidence_score = db.Column(db.Numeric(5, 4), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    user = db.relationship("User", back_populates="image_analyses")
    predicted_body_type = db.relationship("BodyTypeCategory", back_populates="image_analyses")
    recommendations = db.relationship("UserRecommendation", back_populates="analysis")

    def __repr__(self) -> str:
        return f"<ImageAnalysisRecord {self.analysis_id}>"
