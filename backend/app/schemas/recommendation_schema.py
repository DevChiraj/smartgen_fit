"""Response shape for the dashboard's latest-recommendation widget.

Module 11 replaced the minimal template-plan summary with the full
matched meal + workout record (the KNN match's entire row from each
dataset) - the dashboard now displays this directly rather than linking
out to separate plan-detail pages, per the project owner's explicit
Module 11 request.
"""

from marshmallow import Schema, fields


class BodyTypeSummarySchema(Schema):
    body_type_id = fields.Integer()
    name = fields.String()


class MatchedMealRecordSchema(Schema):
    person_id = fields.String()
    age = fields.Integer()
    gender = fields.String()
    bmi = fields.Decimal(as_string=True)
    bmi_category = fields.String()
    breakfast = fields.String()
    morning_snack = fields.String()
    lunch = fields.String()
    evening_snack = fields.String()
    dinner = fields.String()
    daily_calories = fields.Integer()


class MatchedWorkoutRecordSchema(Schema):
    person_id = fields.String()
    fitness_level = fields.String()
    workout_type = fields.String()
    workout_category = fields.String()
    intensity = fields.String()
    duration_min = fields.Integer()
    days_per_week = fields.Integer()
    calories_burned = fields.Integer()
    target_muscle = fields.String()
    equipment = fields.String(allow_none=True)
    indoor_outdoor = fields.String()
    goal = fields.String()
    warmup_min = fields.Integer()
    cooldown_min = fields.Integer()


class LatestRecommendationSchema(Schema):
    recommendation_id = fields.Integer()
    bmi_value = fields.Decimal(as_string=True)
    created_at = fields.DateTime()
    body_type = fields.Nested(BodyTypeSummarySchema, attribute="analysis.predicted_body_type")
    matched_person_id = fields.String()
    meal_record = fields.Nested(MatchedMealRecordSchema, attribute="matched_meal_record")
    workout_record = fields.Nested(MatchedWorkoutRecordSchema, attribute="matched_workout_record")
