"""Request/response orchestration for image analysis endpoints."""

from app.schemas.image_analysis_schema import ImageAnalysisRecordSchema
from app.services import image_analysis_service

record_schema = ImageAnalysisRecordSchema()
records_schema = ImageAnalysisRecordSchema(many=True)


def handle_analyze(user_id: str, file):
    record = image_analysis_service.analyze(int(user_id), file)
    return {"analysis": record_schema.dump(record)}, 201


def handle_get_history(user_id: str):
    records = image_analysis_service.get_history(int(user_id))
    return {"history": records_schema.dump(records)}, 200
