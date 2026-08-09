"""Request/response validation for the workout tracker endpoints."""

from marshmallow import Schema, fields, validate


class WorkoutLogCreateSchema(Schema):
    exercise_id = fields.Integer(required=True, validate=validate.Range(min=1))
    log_date = fields.Date(load_default=None)
    duration_minutes = fields.Integer(required=True, validate=validate.Range(min=1, max=600))
    calories_burned = fields.Integer(
        load_default=None, allow_none=True, validate=validate.Range(min=0, max=5000)
    )
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=255))


class ExerciseSummarySchema(Schema):
    exercise_id = fields.Integer()
    exercise_name = fields.String()
    target_muscle = fields.String()


class WorkoutLogSchema(Schema):
    log_id = fields.Integer()
    log_date = fields.Date()
    duration_minutes = fields.Integer()
    calories_burned = fields.Integer()
    notes = fields.String(allow_none=True)
    created_at = fields.DateTime()
    exercise = fields.Nested(ExerciseSummarySchema)
