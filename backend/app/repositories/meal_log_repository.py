"""DB access for user meal logs."""

from datetime import date

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


def has_any_logs(user_id: int) -> bool:
    return db.session.query(MealLog.query.filter_by(user_id=user_id).exists()).scalar()


def get_for_date(user_id: int, log_date: date) -> list[MealLog]:
    return MealLog.query.filter_by(user_id=user_id, log_date=log_date).all()


def get_meal_types_for_date(user_id: int, log_date: date) -> set[str]:
    rows = (
        MealLog.query.filter_by(user_id=user_id, log_date=log_date)
        .with_entities(MealLog.meal_type)
        .distinct()
        .all()
    )
    return {row[0] for row in rows}
