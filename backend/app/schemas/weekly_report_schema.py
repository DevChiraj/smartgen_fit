"""Response shape for the Weekly Health Report endpoint. The PDF itself is
generated client-side (jsPDF); this just aggregates the real data behind it.
"""

from marshmallow import Schema, fields

from app.schemas.image_analysis_schema import ImageAnalysisRecordSchema
from app.schemas.recommendation_schema import LatestRecommendationSchema
from app.schemas.user_schema import UserPublicSchema


class BmiCategorySummarySchema(Schema):
    category_name = fields.String()
    min_bmi = fields.Decimal(as_string=True)
    max_bmi = fields.Decimal(as_string=True)


class WeeklyTotalsSchema(Schema):
    start_date = fields.Date()
    end_date = fields.Date()
    calories_consumed = fields.Integer()
    calories_burned = fields.Integer()
    workouts_logged = fields.Integer()
    meals_logged = fields.Integer()
    protein_g = fields.Decimal(as_string=True)


class WeeklyReportSchema(Schema):
    user = fields.Nested(UserPublicSchema)
    bmi_value = fields.Decimal(as_string=True, allow_none=True)
    bmi_category = fields.Nested(BmiCategorySummarySchema, allow_none=True)
    latest_analysis = fields.Nested(ImageAnalysisRecordSchema, allow_none=True)
    recommendation = fields.Nested(LatestRecommendationSchema, allow_none=True)
    totals = fields.Nested(WeeklyTotalsSchema)
