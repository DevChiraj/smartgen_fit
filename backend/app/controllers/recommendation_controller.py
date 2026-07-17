"""Request/response orchestration for the dashboard's recommendation widget."""

from app.schemas.recommendation_schema import LatestRecommendationSchema
from app.services import recommendation_service

latest_recommendation_schema = LatestRecommendationSchema()


def handle_get_latest(user_id: str):
    recommendation = recommendation_service.get_latest_recommendation(int(user_id))
    body = latest_recommendation_schema.dump(recommendation) if recommendation is not None else None
    return {"recommendation": body}, 200
