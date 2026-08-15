"""Idempotent seed data: reference tables + a handful of sample plans, plus
the Module 12 Kaggle-sourced Sri Lankan food nutrition data and the
Module 13 Kaggle-sourced exercise library.
"""

import click

from app.extensions import db
from app.models import (
    AgeGroup,
    BMICategory,
    BodyTypeCategory,
    Exercise,
    MealPlan,
    SriLankanFood,
    WorkoutPlan,
)
from app.seed_exercise_data import load_exercise_records
from app.seed_food_data import load_food_records

BODY_TYPES = [
    ("Thin", "Below-average body mass; benefits from a calorie surplus and strength training."),
    ("Normal", "Healthy body composition; benefits from a maintenance-calorie, balanced routine."),
    ("Overweight", "Above-average body mass; benefits from a calorie deficit and cardio training."),
]

BMI_CATEGORIES = [
    ("Underweight", 0.0, 18.5),
    ("Normal weight", 18.5, 25.0),
    ("Overweight", 25.0, 30.0),
    ("Obese", 30.0, 60.0),
]

AGE_GROUPS = [
    ("Teenager", 15, 19),
    ("Adult", 20, 59),
    ("Senior", 60, 120),
]

# (body_type_name, bmi_category_name, age_group_name, gender) -> plan content
MEAL_PLANS = [
    dict(
        plan_code="MP-THIN-UW-ADULT-M",
        lookup=("Thin", "Underweight", "Adult", "male"),
        breakfast="String hoppers with dhal curry and egg hopper",
        lunch="Red rice, chicken curry, jackfruit curry, coconut sambol",
        dinner="Red rice, fish curry, green gram curry",
        snacks="Papaya, roasted peanuts",
        calories=2800,
        protein_g=110,
        carbs_g=380,
        fat_g=90,
        fiber_g=35,
        vitamins="B-complex, C, D",
        minerals="Iron, Calcium, Magnesium",
        daily_water_ml=2500,
    ),
    dict(
        plan_code="MP-THIN-UW-ADULT-F",
        lookup=("Thin", "Underweight", "Adult", "female"),
        breakfast="Egg hopper with coconut sambol and papaya",
        lunch="Red rice, dhal curry, chicken curry, gotu kola sambol",
        dinner="String hoppers, fish curry, jackfruit curry",
        snacks="Green gram curry, papaya",
        calories=2400,
        protein_g=95,
        carbs_g=320,
        fat_g=75,
        fiber_g=32,
        vitamins="B-complex, C, D, Folate",
        minerals="Iron, Calcium",
        daily_water_ml=2200,
    ),
    dict(
        plan_code="MP-NORM-NW-ADULT-M",
        lookup=("Normal", "Normal weight", "Adult", "male"),
        breakfast="String hoppers with dhal curry",
        lunch="Red rice, chicken curry, gotu kola sambol, papaya",
        dinner="Red rice, fish curry, jackfruit curry",
        snacks="Papaya, green gram curry",
        calories=2200,
        protein_g=90,
        carbs_g=280,
        fat_g=65,
        fiber_g=30,
        vitamins="B-complex, C",
        minerals="Iron, Potassium",
        daily_water_ml=2500,
    ),
    dict(
        plan_code="MP-NORM-NW-ADULT-F",
        lookup=("Normal", "Normal weight", "Adult", "female"),
        breakfast="Egg hopper with papaya",
        lunch="Red rice, dhal curry, fish curry, coconut sambol",
        dinner="String hoppers, chicken curry, gotu kola sambol",
        snacks="Papaya",
        calories=1900,
        protein_g=75,
        carbs_g=240,
        fat_g=55,
        fiber_g=26,
        vitamins="B-complex, C, Folate",
        minerals="Iron, Calcium",
        daily_water_ml=2200,
    ),
    dict(
        plan_code="MP-OVWT-OW-ADULT-M",
        lookup=("Overweight", "Overweight", "Adult", "male"),
        breakfast="Gotu kola sambol with string hoppers (2 pcs)",
        lunch="Red rice (small), fish curry, jackfruit curry, green gram curry",
        dinner="Dhal curry, gotu kola sambol, papaya",
        snacks="Papaya",
        calories=1800,
        protein_g=100,
        carbs_g=180,
        fat_g=45,
        fiber_g=34,
        vitamins="B-complex, C",
        minerals="Iron, Potassium, Magnesium",
        daily_water_ml=2800,
    ),
    dict(
        plan_code="MP-OVWT-OW-ADULT-F",
        lookup=("Overweight", "Overweight", "Adult", "female"),
        breakfast="Papaya with green gram curry",
        lunch="Red rice (small), chicken curry, gotu kola sambol",
        dinner="Dhal curry, jackfruit curry, coconut sambol (light)",
        snacks="Papaya",
        calories=1500,
        protein_g=85,
        carbs_g=150,
        fat_g=38,
        fiber_g=30,
        vitamins="B-complex, C, Folate",
        minerals="Iron, Calcium",
        daily_water_ml=2500,
    ),
]

WORKOUT_PLANS = [
    dict(
        plan_code="WP-THIN-UW-ADULT-M",
        lookup=("Thin", "Underweight", "Adult", "male"),
        warm_up="5 min brisk walk + dynamic stretches",
        cardio="10 min light cycling",
        strength_training="Compound lifts (squat, deadlift, bench press) 4x8, progressive overload",
        stretching="Full-body static stretch",
        cool_down="5 min slow walk + deep breathing",
        duration_minutes=60,
        repetitions="4 sets x 8 reps",
        weekly_schedule="Mon/Wed/Fri/Sat",
        calories_burned=350,
    ),
    dict(
        plan_code="WP-THIN-UW-ADULT-F",
        lookup=("Thin", "Underweight", "Adult", "female"),
        warm_up="5 min brisk walk + joint mobility",
        cardio="10 min light cycling",
        strength_training="Bodyweight + resistance band circuit 3x10, progressive overload",
        stretching="Full-body static stretch",
        cool_down="5 min slow walk + deep breathing",
        duration_minutes=50,
        repetitions="3 sets x 10 reps",
        weekly_schedule="Mon/Wed/Fri",
        calories_burned=300,
    ),
    dict(
        plan_code="WP-NORM-NW-ADULT-M",
        lookup=("Normal", "Normal weight", "Adult", "male"),
        warm_up="5 min jog + dynamic stretches",
        cardio="20 min moderate jogging or cycling",
        strength_training="Full-body circuit 3x12",
        stretching="Full-body static stretch",
        cool_down="5 min walk + breathing",
        duration_minutes=60,
        repetitions="3 sets x 12 reps",
        weekly_schedule="Mon/Tue/Thu/Sat",
        calories_burned=450,
    ),
    dict(
        plan_code="WP-NORM-NW-ADULT-F",
        lookup=("Normal", "Normal weight", "Adult", "female"),
        warm_up="5 min jog + dynamic stretches",
        cardio="20 min moderate cycling or swimming",
        strength_training="Full-body circuit 3x12",
        stretching="Full-body static stretch",
        cool_down="5 min walk + breathing",
        duration_minutes=55,
        repetitions="3 sets x 12 reps",
        weekly_schedule="Mon/Tue/Thu/Sat",
        calories_burned=400,
    ),
    dict(
        plan_code="WP-OVWT-OW-ADULT-M",
        lookup=("Overweight", "Overweight", "Adult", "male"),
        warm_up="8 min brisk walk + dynamic stretches",
        cardio="30 min moderate cycling or brisk walking",
        strength_training="Bodyweight circuit (squats, push-ups, lunges) 3x15",
        stretching="Full-body static stretch",
        cool_down="8 min slow walk + breathing",
        duration_minutes=70,
        repetitions="3 sets x 15 reps",
        weekly_schedule="Mon/Tue/Wed/Fri/Sat",
        calories_burned=550,
    ),
    dict(
        plan_code="WP-OVWT-OW-ADULT-F",
        lookup=("Overweight", "Overweight", "Adult", "female"),
        warm_up="8 min brisk walk + dynamic stretches",
        cardio="25 min moderate cycling or swimming",
        strength_training="Bodyweight circuit (squats, wall push-ups, lunges) 3x15",
        stretching="Full-body static stretch",
        cool_down="8 min slow walk + breathing",
        duration_minutes=65,
        repetitions="3 sets x 15 reps",
        weekly_schedule="Mon/Tue/Wed/Fri/Sat",
        calories_burned=480,
    ),
]


def _get_or_create_reference_tables():
    body_types = {}
    for name, description in BODY_TYPES:
        obj = BodyTypeCategory.query.filter_by(name=name).first()
        if obj is None:
            obj = BodyTypeCategory(name=name, description=description)
            db.session.add(obj)
            db.session.flush()
        body_types[name] = obj

    bmi_categories = {}
    for name, min_bmi, max_bmi in BMI_CATEGORIES:
        obj = BMICategory.query.filter_by(category_name=name).first()
        if obj is None:
            obj = BMICategory(category_name=name, min_bmi=min_bmi, max_bmi=max_bmi)
            db.session.add(obj)
            db.session.flush()
        bmi_categories[name] = obj

    age_groups = {}
    for name, min_age, max_age in AGE_GROUPS:
        obj = AgeGroup.query.filter_by(name=name).first()
        if obj is None:
            obj = AgeGroup(name=name, min_age=min_age, max_age=max_age)
            db.session.add(obj)
            db.session.flush()
        age_groups[name] = obj

    return body_types, bmi_categories, age_groups


def _seed_foods():
    # Drop the pre-Module-12 manually-curated placeholder rows (identifiable by
    # having no serving_size - every Kaggle-sourced row below always sets one)
    # so re-running `flask seed` on a database seeded before this module
    # converges to the same real dataset instead of keeping both.
    SriLankanFood.query.filter(SriLankanFood.serving_size.is_(None)).delete()

    for food in load_food_records():
        if SriLankanFood.query.filter_by(food_name=food["food_name"]).first() is None:
            db.session.add(SriLankanFood(**food))


def _seed_exercises():
    for exercise in load_exercise_records():
        if Exercise.query.filter_by(exercise_name=exercise["exercise_name"]).first() is None:
            db.session.add(Exercise(**exercise))


def _seed_meal_plans(body_types, bmi_categories, age_groups):
    for plan in MEAL_PLANS:
        if MealPlan.query.filter_by(plan_code=plan["plan_code"]).first() is not None:
            continue
        body_type_name, bmi_category_name, age_group_name, gender = plan["lookup"]
        db.session.add(
            MealPlan(
                plan_code=plan["plan_code"],
                body_type_id=body_types[body_type_name].body_type_id,
                bmi_category_id=bmi_categories[bmi_category_name].bmi_category_id,
                age_group_id=age_groups[age_group_name].age_group_id,
                gender=gender,
                breakfast=plan["breakfast"],
                lunch=plan["lunch"],
                dinner=plan["dinner"],
                snacks=plan["snacks"],
                calories=plan["calories"],
                protein_g=plan["protein_g"],
                carbs_g=plan["carbs_g"],
                fat_g=plan["fat_g"],
                fiber_g=plan["fiber_g"],
                vitamins=plan["vitamins"],
                minerals=plan["minerals"],
                daily_water_ml=plan["daily_water_ml"],
            )
        )


def _seed_workout_plans(body_types, bmi_categories, age_groups):
    for plan in WORKOUT_PLANS:
        if WorkoutPlan.query.filter_by(plan_code=plan["plan_code"]).first() is not None:
            continue
        body_type_name, bmi_category_name, age_group_name, gender = plan["lookup"]
        db.session.add(
            WorkoutPlan(
                plan_code=plan["plan_code"],
                body_type_id=body_types[body_type_name].body_type_id,
                bmi_category_id=bmi_categories[bmi_category_name].bmi_category_id,
                age_group_id=age_groups[age_group_name].age_group_id,
                gender=gender,
                warm_up=plan["warm_up"],
                cardio=plan["cardio"],
                strength_training=plan["strength_training"],
                stretching=plan["stretching"],
                cool_down=plan["cool_down"],
                duration_minutes=plan["duration_minutes"],
                repetitions=plan["repetitions"],
                weekly_schedule=plan["weekly_schedule"],
                calories_burned=plan["calories_burned"],
            )
        )


def seed_data():
    """Populate reference tables and sample plans/foods. Safe to run repeatedly."""
    body_types, bmi_categories, age_groups = _get_or_create_reference_tables()
    _seed_foods()
    _seed_exercises()
    _seed_meal_plans(body_types, bmi_categories, age_groups)
    _seed_workout_plans(body_types, bmi_categories, age_groups)
    db.session.commit()


def register_seed_command(app):
    @app.cli.command("seed")
    def seed_command():
        """Populate the database with reference data and sample plans/foods."""
        seed_data()
        click.echo("Database seeded.")
