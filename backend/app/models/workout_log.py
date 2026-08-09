"""Daily workout log entries - a real user-logged history of completed
workouts. Distinct from the Module 11 KNN-matched plan (aspirational, not
logged) and the Module 13 exercises library (reference-only, standalone).
Each entry ties back to a real exercises row rather than free text.
"""

from app.extensions import db
from app.models.mixins import utcnow


class WorkoutLog(db.Model):
    __tablename__ = "workout_logs"

    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.exercise_id"), nullable=False)
    log_date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    calories_burned = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    user = db.relationship("User", back_populates="workout_logs")
    exercise = db.relationship("Exercise")

    def __repr__(self) -> str:
        return f"<WorkoutLog {self.log_id}>"
