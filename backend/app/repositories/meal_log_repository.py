"""DB access for user meal logs."""

from app.extensions import db
from app.models import MealLog

HISTORY_LIMIT = 100


def create(**kwargs) -> MealLog:
    log = MealLog(**kwargs)
    db.session.add(log)
    db.session.commit()
    return log


def get_history_for_user(user_id: int) -> list[MealLog]:
    return (
        MealLog.query.filter_by(user_id=user_id)
        .order_by(MealLog.log_date.desc(), MealLog.log_id.desc())
        .limit(HISTORY_LIMIT)
        .all()
    )
