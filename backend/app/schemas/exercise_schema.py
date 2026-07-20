"""Response shape for the public Workouts browsing/search page."""

from marshmallow import Schema, fields


class ExerciseSchema(Schema):
    exercise_id = fields.Integer()
    exercise_name = fields.String()
    target_muscle = fields.String()
    difficulty = fields.String()
    equipment = fields.String(allow_none=True)
    sets = fields.Integer()
    reps = fields.Integer()
    calories_per_30min = fields.Integer()
    benefit = fields.String()
