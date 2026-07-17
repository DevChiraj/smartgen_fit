"""Read-only access to a user's recommendation history for the dashboard.

Creating recommendations (the rule-based lookup triggered after image
classification) is RecommendationService's job in Module 11 - this
module only reads what already exists.
"""

from app.models import UserRecommendation
from app.repositories import recommendation_repository


def get_latest_recommendation(user_id: int) -> UserRecommendation | None:
    return recommendation_repository.get_latest_for_user(user_id)
