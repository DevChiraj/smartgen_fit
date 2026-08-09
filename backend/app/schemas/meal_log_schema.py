"""Request/response validation for the meal diary endpoints."""

from decimal import Decimal

from marshmallow import Schema, fields, validate

from app.models.meal_log import MEAL_TYPES


class MealLogCreateSchema(Schema):
    food_id = fields.Integer(required=True, validate=validate.Range(min=1))
    meal_type = fields.String(required=True, validate=validate.OneOf(MEAL_TYPES))
    log_date = fields.Date(load_default=None)
    quantity_servings = fields.Decimal(
        load_default=Decimal("1"),
        validate=validate.Range(min=Decimal("0.1"), max=Decimal("20")),
    )
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=255))


class FoodSummarySchema(Schema):
    food_id = fields.Integer()
    food_name = fields.String()
    category = fields.String()


class MealLogSchema(Schema):
    log_id = fields.Integer()
    meal_type = fields.String()
    log_date = fields.Date()
    quantity_servings = fields.Decimal(as_string=True)
    calories = fields.Integer()
    protein_g = fields.Decimal(as_string=True)
    notes = fields.String(allow_none=True)
    created_at = fields.DateTime()
    food = fields.Nested(FoodSummarySchema)
