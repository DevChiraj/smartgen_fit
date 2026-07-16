"""Registry of trained CNN model files (admins manage data without ever retraining)."""

from app.extensions import db
from app.models.mixins import utcnow


class AIModelFile(db.Model):
    __tablename__ = "ai_model_files"

    model_id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(50), unique=True, nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    accuracy = db.Column(db.Numeric(5, 4), nullable=True)
    trained_date = db.Column(db.DateTime, nullable=False, default=utcnow)
    is_active = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        return f"<AIModelFile {self.version}>"
