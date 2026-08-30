"""Request/response orchestration for the dashboard's recommendation widget."""

from app.repositories import workout_recommendation_repository
from app.schemas.recommendation_schema import LatestRecommendationSchema
from app.services import recommendation_service

latest_recommendation_schema = LatestRecommendationSchema()


def handle_get_latest(user_id: str):
    recommendation = recommendation_service.get_latest_recommendation(int(user_id))
    if recommendation is None:
        return {"recommendation": None}, 200

    # matched_workout_record isn't a real relationship (no direct FK column
    # on user_recommendations - see app/models/user_recommendation.py), so
    # it's attached transiently here for the schema to read.
    recommendation.matched_workout_record = (
        workout_recommendation_repository.get_by_person_id(recommendation.matched_person_id)
        if recommendation.matched_person_id is not None
        else None
    )
    body = latest_recommendation_schema.dump(recommendation)
    return {"recommendation": body}, 200
