"""DB access for sri_lankan_foods."""

from sqlalchemy import func

from app.extensions import db
from app.models import SriLankanFood


def get_all(category: str | None = None, search: str | None = None) -> list[SriLankanFood]:
    query = SriLankanFood.query
    if category:
        query = query.filter(func.lower(SriLankanFood.category) == category.lower())
    if search:
        query = query.filter(SriLankanFood.food_name.ilike(f"%{search}%"))
    return query.order_by(SriLankanFood.food_name).all()


def get_by_id(food_id: int) -> SriLankanFood | None:
    return db.session.get(SriLankanFood, food_id)


def get_categories() -> list[str]:
    rows = SriLankanFood.query.with_entities(SriLankanFood.category).distinct().all()
    return sorted(row[0] for row in rows)
