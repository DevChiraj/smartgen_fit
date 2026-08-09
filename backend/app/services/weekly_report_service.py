"""Aggregates the data behind the Weekly Health Report PDF: the user's
profile, BMI, latest body-type scan, latest matched meal/workout plan, and
the last 7 days' logged calories consumed vs burned. Read-only, composes
existing repositories/services rather than duplicating their logic - the
PDF itself is generated client-side (jsPDF) from this one payload.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from app.models import BMICategory, ImageAnalysisRecord, User, UserRecommendation
from app.repositories import (
    image_analysis_repository,
    meal_log_repository,
    recommendation_repository,
    workout_log_repository,
    workout_recommendation_repository,
)
from app.services import bmi_service

REPORT_WINDOW_DAYS = 7


@dataclass
class WeeklyTotals:
    start_date: date
    end_date: date
    calories_consumed: int
    calories_burned: int
    workouts_logged: int
    meals_logged: int
    protein_g: Decimal


@dataclass
class WeeklyReport:
    user: User
    bmi_value: Decimal | None
    bmi_category: BMICategory | None
    latest_analysis: ImageAnalysisRecord | None
    recommendation: UserRecommendation | None
    totals: WeeklyTotals


def _weekly_totals(user_id: int, today: date) -> WeeklyTotals:
    start = today - timedelta(days=REPORT_WINDOW_DAYS - 1)
    workout_logs = workout_log_repository.get_for_user_since(user_id, start)
    meal_logs = meal_log_repository.get_for_user_since(user_id, start)

    return WeeklyTotals(
        start_date=start,
        end_date=today,
        calories_consumed=sum(log.calories for log in meal_logs),
        calories_burned=sum(log.calories_burned for log in workout_logs),
        workouts_logged=len(workout_logs),
        meals_logged=len(meal_logs),
        protein_g=sum((log.protein_g for log in meal_logs), Decimal("0")),
    )


def get_weekly_report(user: User) -> WeeklyReport:
    bmi_value = None
    bmi_category = None
    if user.height_cm is not None and user.weight_kg is not None:
        bmi_value = bmi_service.calculate_bmi(user.height_cm, user.weight_kg)
        bmi_category = bmi_service.classify_bmi(bmi_value)

    history = image_analysis_repository.get_history_for_user(user.user_id)
    latest_analysis = history[0] if history else None

    recommendation = recommendation_repository.get_latest_for_user(user.user_id)
    if recommendation is not None and recommendation.matched_person_id is not None:
        recommendation.matched_workout_record = workout_recommendation_repository.get_by_person_id(
            recommendation.matched_person_id
        )

    totals = _weekly_totals(user.user_id, date.today())

    return WeeklyReport(
        user=user,
        bmi_value=bmi_value,
        bmi_category=bmi_category,
        latest_analysis=latest_analysis,
        recommendation=recommendation,
        totals=totals,
    )
