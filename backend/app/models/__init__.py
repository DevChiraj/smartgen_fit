"""Import every model so Alembic autogenerate and db.create_all() can see them all."""

from app.models.age_group import AgeGroup
from app.models.ai_model_file import AIModelFile
from app.models.bmi_category import BMICategory
from app.models.body_type_category import BodyTypeCategory
from app.models.exercise import Exercise
from app.models.image_analysis_record import ImageAnalysisRecord
from app.models.meal_plan import MealPlan
from app.models.meal_recommendation_record import MealRecommendationRecord
from app.models.sri_lankan_food import SriLankanFood
from app.models.user import User
from app.models.user_recommendation import UserRecommendation
from app.models.workout_log import WorkoutLog
from app.models.workout_plan import WorkoutPlan
from app.models.workout_recommendation_record import WorkoutRecommendationRecord

__all__ = [
    "AgeGroup",
    "AIModelFile",
    "BMICategory",
    "BodyTypeCategory",
    "Exercise",
    "ImageAnalysisRecord",
    "MealPlan",
    "MealRecommendationRecord",
    "SriLankanFood",
    "User",
    "UserRecommendation",
    "WorkoutLog",
    "WorkoutPlan",
    "WorkoutRecommendationRecord",
]
