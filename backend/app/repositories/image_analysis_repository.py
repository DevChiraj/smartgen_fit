"""DB access for image analysis records."""

from app.extensions import db
from app.models import ImageAnalysisRecord

HISTORY_LIMIT = 20


def create(**kwargs) -> ImageAnalysisRecord:
    record = ImageAnalysisRecord(**kwargs)
    db.session.add(record)
    db.session.commit()
    return record


def get_history_for_user(user_id: int) -> list[ImageAnalysisRecord]:
    return (
        ImageAnalysisRecord.query.filter_by(user_id=user_id)
        .order_by(ImageAnalysisRecord.created_at.desc(), ImageAnalysisRecord.analysis_id.desc())
        .limit(HISTORY_LIMIT)
        .all()
    )
