"""Request/response validation for admin-only management endpoints
(Module 14). Separate from the public read schemas (food_schema.py,
exercise_schema.py) since admin write payloads have different
requirements (e.g. required-on-create vs. optional-on-update) and admin
responses expose fields (role, email) the public endpoints don't.
"""

from marshmallow import EXCLUDE, Schema, fields, validate


class AdminUserSchema(Schema):
    user_id = fields.Integer()
    full_name = fields.String()
    username = fields.String()
    email = fields.String()
    gender = fields.String()
    age = fields.Integer()
    phone_number = fields.String(allow_none=True)
    height_cm = fields.Decimal(as_string=True, allow_none=True)
    weight_kg = fields.Decimal(as_string=True, allow_none=True)
    role = fields.String()
    created_at = fields.DateTime()


class AdminUserUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    full_name = fields.String(required=False, validate=validate.Length(min=2, max=150))
    phone_number = fields.String(required=False, allow_none=True, validate=validate.Length(max=20))
    height_cm = fields.Decimal(required=False, allow_none=True, places=2)
    weight_kg = fields.Decimal(required=False, allow_none=True, places=2)
    role = fields.String(required=False, validate=validate.OneOf(["user", "admin"]))


class SriLankanFoodWriteSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    food_name = fields.String(required=True, validate=validate.Length(min=1, max=150))
    category = fields.String(required=True, validate=validate.Length(min=1, max=50))
    serving_size = fields.String(required=False, allow_none=True, validate=validate.Length(max=50))
    calories = fields.Integer(required=True, validate=validate.Range(min=0))
    protein_g = fields.Decimal(required=True, validate=validate.Range(min=0))
    carbs_g = fields.Decimal(required=True, validate=validate.Range(min=0))
    fat_g = fields.Decimal(required=True, validate=validate.Range(min=0))
    fiber_g = fields.Decimal(required=False, allow_none=True, validate=validate.Range(min=0))
    vitamins = fields.String(required=False, allow_none=True, validate=validate.Length(max=255))
    minerals = fields.String(required=False, allow_none=True, validate=validate.Length(max=255))
    image_url = fields.String(required=False, allow_none=True, validate=validate.Length(max=255))


class ExerciseWriteSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    exercise_name = fields.String(required=True, validate=validate.Length(min=1, max=150))
    target_muscle = fields.String(required=True, validate=validate.Length(min=1, max=150))
    difficulty = fields.String(
        required=True, validate=validate.OneOf(["Beginner", "Intermediate", "Advanced"])
    )
    equipment = fields.String(required=False, allow_none=True, validate=validate.Length(max=100))
    sets = fields.Integer(required=True, validate=validate.Range(min=1))
    reps = fields.Integer(required=True, validate=validate.Range(min=1))
    calories_per_30min = fields.Integer(required=True, validate=validate.Range(min=0))
    benefit = fields.String(required=True, validate=validate.Length(min=1, max=255))


class BodyTypeCategorySchema(Schema):
    body_type_id = fields.Integer()
    name = fields.String()
    description = fields.String()


class BodyTypeUpdateSchema(Schema):
    """Description only - `name` stays fixed since ai_model's CLASS_NAMES
    (Thin/Normal/Overweight) and body_type_repository.get_by_name() key
    image_analysis_service's classification lookup on it directly."""

    class Meta:
        unknown = EXCLUDE

    description = fields.String(required=True, validate=validate.Length(min=1, max=500))


class BMICategoryWriteSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    category_name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    min_bmi = fields.Decimal(required=True, validate=validate.Range(min=0))
    max_bmi = fields.Decimal(required=True, validate=validate.Range(min=0))
