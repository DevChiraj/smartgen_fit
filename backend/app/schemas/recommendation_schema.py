"""Response shape for the dashboard's latest-recommendation widget.

Deliberately minimal - full plan detail (breakfast/lunch/dinner text,
warm-up/cardio/etc.) belongs to the meal/workout plan detail
endpoints Modules 12/13 will add, not the dashboard summary.
"""

from marshmallow import Schema, fields


class BodyTypeSummarySchema(Schema):
    body_type_id = fields.Integer()
    name = fields.String()


class MealPlanSummarySchema(Schema):
    meal_plan_id = fields.Integer()
    plan_code = fields.String()
    calories = fields.Integer()


class WorkoutPlanSummarySchema(Schema):
    workout_plan_id = fields.Integer()
    plan_code = fields.String()
    duration_minutes = fields.Integer()
    calories_burned = fields.Integer()


class LatestRecommendationSchema(Schema):
    recommendation_id = fields.Integer()
    bmi_value = fields.Decimal(as_string=True)
    created_at = fields.DateTime()
    body_type = fields.Nested(BodyTypeSummarySchema, attribute="analysis.predicted_body_type")
    meal_plan = fields.Nested(MealPlanSummarySchema)
    workout_plan = fields.Nested(WorkoutPlanSummarySchema)
