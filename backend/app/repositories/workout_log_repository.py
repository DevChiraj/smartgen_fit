"""DB access for user workout logs."""

from app.extensions import db
from app.models import WorkoutLog

HISTORY_LIMIT = 50


def create(**kwargs) -> WorkoutLog:
    log = WorkoutLog(**kwargs)
    db.session.add(log)
    db.session.commit()
    return log


def get_history_for_user(user_id: int) -> list[WorkoutLog]:
    return (
        WorkoutLog.query.filter_by(user_id=user_id)
        .order_by(WorkoutLog.log_date.desc(), WorkoutLog.log_id.desc())
        .limit(HISTORY_LIMIT)
        .all()
    )
