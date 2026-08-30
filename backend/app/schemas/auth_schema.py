"""Request/response validation for the auth endpoints."""

from marshmallow import Schema, fields, validate

USERNAME_REGEX = r"^[a-zA-Z0-9_]{3,50}$"


class RegisterSchema(Schema):
    full_name = fields.String(required=True, validate=validate.Length(min=2, max=150))
    date_of_birth = fields.Date(required=True)
    gender = fields.String(required=True, validate=validate.OneOf(["male", "female", "other"]))
    email = fields.Email(required=True)
    phone_number = fields.String(required=False, allow_none=True, validate=validate.Length(max=20))
    height_cm = fields.Decimal(required=False, allow_none=True, places=2)
    weight_kg = fields.Decimal(required=False, allow_none=True, places=2)
    username = fields.String(required=True, validate=validate.Regexp(USERNAME_REGEX))
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=8))


class LoginSchema(Schema):
    identifier = fields.String(required=True)
    password = fields.String(required=True, load_only=True)
