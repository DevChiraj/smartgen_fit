"""User account model."""

from app.extensions import db
from app.models.mixins import TimestampMixin


class User(db.Model, TimestampMixin):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(20), nullable=True)
    height_cm = db.Column(db.Numeric(5, 2), nullable=True)
    weight_kg = db.Column(db.Numeric(5, 2), nullable=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_picture_url = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), nullable=False, default="user")

    image_analyses = db.relationship(
        "ImageAnalysisRecord", back_populates="user", cascade="all, delete-orphan"
    )
    recommendations = db.relationship(
        "UserRecommendation", back_populates="user", cascade="all, delete-orphan"
    )
    workout_logs = db.relationship(
        "WorkoutLog", back_populates="user", cascade="all, delete-orphan"
    )
    meal_logs = db.relationship("MealLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.username}>"
