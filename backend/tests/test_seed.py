from app.models import AgeGroup, BMICategory, BodyTypeCategory, MealPlan, SriLankanFood, WorkoutPlan
from app.seed import (
    AGE_GROUPS,
    BMI_CATEGORIES,
    BODY_TYPES,
    MEAL_PLANS,
    SRI_LANKAN_FOODS,
    WORKOUT_PLANS,
)
from app.seed import seed_data


def test_seed_data_populates_expected_counts(app, db):
    seed_data()

    assert BodyTypeCategory.query.count() == len(BODY_TYPES)
    assert BMICategory.query.count() == len(BMI_CATEGORIES)
    assert AgeGroup.query.count() == len(AGE_GROUPS)
    assert SriLankanFood.query.count() == len(SRI_LANKAN_FOODS)
    assert MealPlan.query.count() == len(MEAL_PLANS)
    assert WorkoutPlan.query.count() == len(WORKOUT_PLANS)


def test_seed_data_is_idempotent(app, db):
    seed_data()
    seed_data()

    assert BodyTypeCategory.query.count() == len(BODY_TYPES)
    assert MealPlan.query.count() == len(MEAL_PLANS)
    assert WorkoutPlan.query.count() == len(WORKOUT_PLANS)
    assert SriLankanFood.query.count() == len(SRI_LANKAN_FOODS)
