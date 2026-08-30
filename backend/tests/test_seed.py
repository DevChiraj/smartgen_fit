from app.models import (
    AgeGroup,
    BMICategory,
    BodyTypeCategory,
    Exercise,
    MealPlan,
    SriLankanFood,
    WorkoutPlan,
)
from app.seed import AGE_GROUPS, BMI_CATEGORIES, BODY_TYPES, MEAL_PLANS, WORKOUT_PLANS
from app.seed import seed_data
from app.seed_exercise_data import load_exercise_records
from app.seed_food_data import load_food_records

FOOD_COUNT = len(load_food_records())
EXERCISE_COUNT = len(load_exercise_records())


def test_seed_data_populates_expected_counts(app, db):
    seed_data()

    assert BodyTypeCategory.query.count() == len(BODY_TYPES)
    assert BMICategory.query.count() == len(BMI_CATEGORIES)
    assert AgeGroup.query.count() == len(AGE_GROUPS)
    assert SriLankanFood.query.count() == FOOD_COUNT
    assert Exercise.query.count() == EXERCISE_COUNT
    assert MealPlan.query.count() == len(MEAL_PLANS)
    assert WorkoutPlan.query.count() == len(WORKOUT_PLANS)


def test_seed_data_is_idempotent(app, db):
    seed_data()
    seed_data()

    assert BodyTypeCategory.query.count() == len(BODY_TYPES)
    assert MealPlan.query.count() == len(MEAL_PLANS)
    assert WorkoutPlan.query.count() == len(WORKOUT_PLANS)
    assert SriLankanFood.query.count() == FOOD_COUNT
    assert Exercise.query.count() == EXERCISE_COUNT


def test_seed_data_replaces_pre_module_12_placeholder_foods(app, db):
    """A DB seeded before Module 12 had 12 manually-curated rows with no
    serving_size - re-seeding should converge to just the real dataset."""
    db.session.add(
        SriLankanFood(
            food_name="Old placeholder food",
            category="Mixed",
            calories=100,
            protein_g=1,
            carbs_g=1,
            fat_g=1,
        )
    )
    db.session.commit()

    seed_data()

    assert SriLankanFood.query.filter_by(food_name="Old placeholder food").first() is None
    assert SriLankanFood.query.count() == FOOD_COUNT


def test_load_food_records_rejects_a_food_name_with_no_category_mapping(tmp_path):
    import pandas as pd

    from app.seed_food_data import load_food_records

    df = pd.DataFrame(
        [
            {
                "Food": "Totally Unknown Dish",
                "Quantity": "100g",
                "Calories (kcal)": "100 kcal",
                "Carbohydrate (g)": "10g",
                "Protein (g)": "5g",
                "Fat (g)": "2g",
            }
        ]
    )
    path = tmp_path / "unknown_food.xlsx"
    df.to_excel(path, index=False)

    try:
        load_food_records(path)
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "No category mapped" in str(exc)


def test_parse_number_rejects_unparseable_values():
    from app.seed_food_data import _parse_number

    try:
        _parse_number("not-a-number")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "Could not parse a number" in str(exc)
