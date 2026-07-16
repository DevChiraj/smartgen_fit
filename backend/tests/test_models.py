from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import AgeGroup, BMICategory, BodyTypeCategory, MealPlan, User


def _make_reference_rows(db):
    body_type = BodyTypeCategory(name="Normal", description="Healthy body composition.")
    bmi_category = BMICategory(category_name="Normal weight", min_bmi=18.5, max_bmi=25.0)
    age_group = AgeGroup(name="Adult", min_age=20, max_age=59)
    db.session.add_all([body_type, bmi_category, age_group])
    db.session.commit()
    return body_type, bmi_category, age_group


def test_user_requires_unique_email(db):
    user1 = User(
        full_name="Test User",
        date_of_birth=date(2000, 1, 1),
        age=26,
        gender="female",
        email="dup@example.com",
        username="user_one",
        password_hash="hashed",
    )
    db.session.add(user1)
    db.session.commit()

    user2 = User(
        full_name="Another User",
        date_of_birth=date(1999, 1, 1),
        age=27,
        gender="male",
        email="dup@example.com",
        username="user_two",
        password_hash="hashed",
    )
    db.session.add(user2)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_meal_plan_lookup_combination_is_unique(db):
    body_type, bmi_category, age_group = _make_reference_rows(db)

    plan_a = MealPlan(
        plan_code="MP-A",
        body_type_id=body_type.body_type_id,
        bmi_category_id=bmi_category.bmi_category_id,
        age_group_id=age_group.age_group_id,
        gender="male",
        breakfast="x",
        lunch="x",
        dinner="x",
        calories=2000,
        protein_g=80,
        carbs_g=250,
        fat_g=60,
    )
    db.session.add(plan_a)
    db.session.commit()

    plan_b = MealPlan(
        plan_code="MP-B",
        body_type_id=body_type.body_type_id,
        bmi_category_id=bmi_category.bmi_category_id,
        age_group_id=age_group.age_group_id,
        gender="male",
        breakfast="y",
        lunch="y",
        dinner="y",
        calories=1800,
        protein_g=70,
        carbs_g=200,
        fat_g=50,
    )
    db.session.add(plan_b)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_meal_plan_relationship_to_body_type(db):
    body_type, bmi_category, age_group = _make_reference_rows(db)
    plan = MealPlan(
        plan_code="MP-REL",
        body_type_id=body_type.body_type_id,
        bmi_category_id=bmi_category.bmi_category_id,
        age_group_id=age_group.age_group_id,
        gender="female",
        breakfast="x",
        lunch="x",
        dinner="x",
        calories=2000,
        protein_g=80,
        carbs_g=250,
        fat_g=60,
    )
    db.session.add(plan)
    db.session.commit()

    assert plan.body_type.name == "Normal"
    assert plan in body_type.meal_plans
