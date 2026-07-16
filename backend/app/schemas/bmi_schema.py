"""Request/response validation for the BMI calculator endpoint."""

from marshmallow import Schema, fields, validate


class BMICalculateSchema(Schema):
    height_cm = fields.Decimal(required=True, validate=validate.Range(min=50, max=250))
    weight_kg = fields.Decimal(required=True, validate=validate.Range(min=2, max=300))


class BMICategorySchema(Schema):
    bmi_category_id = fields.Integer()
    category_name = fields.String()
    min_bmi = fields.Decimal(as_string=True)
    max_bmi = fields.Decimal(as_string=True)
