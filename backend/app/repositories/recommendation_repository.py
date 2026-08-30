"""DB access for user recommendations."""

from app.extensions import db
from app.models import UserRecommendation


def get_latest_for_user(user_id: int) -> UserRecommendation | None:
    return (
        UserRecommendation.query.filter_by(user_id=user_id)
        .order_by(UserRecommendation.created_at.desc(), UserRecommendation.recommendation_id.desc())
        .first()
    )


def create(**kwargs) -> UserRecommendation:
    record = UserRecommendation(**kwargs)
    db.session.add(record)
    db.session.commit()
    return record
