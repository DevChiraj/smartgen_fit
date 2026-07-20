"""Response shape for the public Healthy Foods browsing/search page."""

from marshmallow import Schema, fields


class SriLankanFoodSchema(Schema):
    food_id = fields.Integer()
    food_name = fields.String()
    category = fields.String()
    serving_size = fields.String(allow_none=True)
    calories = fields.Integer()
    protein_g = fields.Decimal(as_string=True)
    carbs_g = fields.Decimal(as_string=True)
    fat_g = fields.Decimal(as_string=True)
    fiber_g = fields.Decimal(as_string=True, allow_none=True)
    vitamins = fields.String(allow_none=True)
    minerals = fields.String(allow_none=True)
    image_url = fields.String(allow_none=True)
