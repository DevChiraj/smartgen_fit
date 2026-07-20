"""Exercise reference library (Module 13) - public, standalone content for
the Workouts page. Not part of the Module 11 KNN recommendation pipeline;
see workout_recommendation_record.py for the user-matched workout plan.
"""

from app.extensions import db


class Exercise(db.Model):
    __tablename__ = "exercises"

    exercise_id = db.Column(db.Integer, primary_key=True)
    exercise_name = db.Column(db.String(150), nullable=False)
    target_muscle = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    equipment = db.Column(db.String(100), nullable=True)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    calories_per_30min = db.Column(db.Integer, nullable=False)
    benefit = db.Column(db.String(255), nullable=False)

    def __repr__(self) -> str:
        return f"<Exercise {self.exercise_name}>"
