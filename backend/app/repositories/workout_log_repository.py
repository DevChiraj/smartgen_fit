"""DB access for user workout logs."""

from datetime import date

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


def get_most_recent_log_date(user_id: int) -> date | None:
    log = WorkoutLog.query.filter_by(user_id=user_id).order_by(WorkoutLog.log_date.desc()).first()
    return log.log_date if log else None
