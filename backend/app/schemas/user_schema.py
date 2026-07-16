"""Request/response validation for user profile endpoints."""

from marshmallow import EXCLUDE, Schema, fields, validate


class UserPublicSchema(Schema):
    user_id = fields.Integer()
    full_name = fields.String()
    username = fields.String()
    email = fields.String()
    gender = fields.String()
    age = fields.Integer()
    phone_number = fields.String()
    height_cm = fields.Decimal(as_string=True)
    weight_kg = fields.Decimal(as_string=True)
    profile_picture_url = fields.String()
    role = fields.String()
    created_at = fields.DateTime()


class UserUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    full_name = fields.String(required=False, validate=validate.Length(min=2, max=150))
    phone_number = fields.String(required=False, allow_none=True, validate=validate.Length(max=20))
    height_cm = fields.Decimal(required=False, allow_none=True, places=2)
    weight_kg = fields.Decimal(required=False, allow_none=True, places=2)
