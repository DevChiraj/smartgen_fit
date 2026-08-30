"""Response shape for image analysis results and history."""

from marshmallow import Schema, fields


class BodyTypeSummarySchema(Schema):
    body_type_id = fields.Integer()
    name = fields.String()


class ImageAnalysisRecordSchema(Schema):
    analysis_id = fields.Integer()
    image_path = fields.String()
    confidence_score = fields.Decimal(as_string=True)
    created_at = fields.DateTime()
    predicted_body_type = fields.Nested(BodyTypeSummarySchema)
