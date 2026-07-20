"""Generates and reads a user's ML-matched recommendation.

Module 11 replaced the original composite-key rule-based lookup with a
KNN similarity match. image_analysis_service.analyze() calls
match_recommendation() (read-only - resolves the nearest Person_ID and
validates both its meal/workout rows exist) *before* persisting the new
ImageAnalysisRecord, then save_recommendation() afterwards to store the
match. Splitting it this way means a bad match never leaves an
image_analysis_records row with no corresponding recommendation - same
"validate everything before the first write" contract the body-type
lookup in image_analysis_service already follows.

Still respects rule 1: the CNN's job stops at a label; this service is
what decides what to recommend from that label, and ai_model/ has no
idea meal or workout plans exist.
"""

from dataclasses import dataclass
from decimal import Decimal

from app import ml_recommendation
from app.models import ImageAnalysisRecord, MealRecommendationRecord, User, UserRecommendation
from app.models.workout_recommendation_record import WorkoutRecommendationRecord
from app.repositories import (
    meal_recommendation_repository,
    recommendation_repository,
    workout_recommendation_repository,
)
from app.services import bmi_service
from app.utils.exceptions import AppError


class NoRecommenderModelError(AppError):
    status_code = 503


@dataclass
class RecommendationMatch:
    meal_record: MealRecommendationRecord
    workout_record: WorkoutRecommendationRecord


def match_recommendation(user: User, predicted_body_type_label: str) -> RecommendationMatch:
    """Read-only: resolves the nearest Person_ID and both its rows. Raises
    without writing anything if the recommender or the matched rows are
    unavailable."""
    try:
        person_id = ml_recommendation.find_matching_person(
            predicted_body_type_label, user.age, user.gender
        )
    except FileNotFoundError as exc:
        raise NoRecommenderModelError(
            "No trained recommender model is currently available. Run "
            "ai_model/recommendation/train_recommender.py first."
        ) from exc

    meal_record = meal_recommendation_repository.get_by_person_id(person_id)
    if meal_record is None:
        raise AppError(
            f"Recommender matched Person_ID '{person_id}', which has no "
            "meal_recommendation_records row.",
            status_code=500,
        )
    workout_record = workout_recommendation_repository.get_by_person_id(person_id)
    if workout_record is None:
        raise AppError(
            f"Recommender matched Person_ID '{person_id}', which has no "
            "workout_recommendation_records row.",
            status_code=500,
        )

    return RecommendationMatch(meal_record=meal_record, workout_record=workout_record)


def _resolve_bmi_value(user: User, matched_meal_record: MealRecommendationRecord) -> Decimal:
    """Prefers the user's own profile BMI; falls back to the matched
    candidate's BMI when the user hasn't set height/weight yet (both are
    optional profile fields - see app/schemas/user_schema.py)."""
    if user.height_cm is not None and user.weight_kg is not None:
        return bmi_service.calculate_bmi(user.height_cm, user.weight_kg)
    return Decimal(str(matched_meal_record.bmi))


def save_recommendation(
    user: User, analysis: ImageAnalysisRecord, match: RecommendationMatch
) -> UserRecommendation:
    bmi_value = _resolve_bmi_value(user, match.meal_record)
    return recommendation_repository.create(
        user_id=user.user_id,
        analysis_id=analysis.analysis_id,
        matched_person_id=match.meal_record.person_id,
        bmi_value=bmi_value,
    )


def get_latest_recommendation(user_id: int) -> UserRecommendation | None:
    return recommendation_repository.get_latest_for_user(user_id)
