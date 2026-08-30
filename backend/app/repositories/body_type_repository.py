"""DB access for body type categories."""

from sqlalchemy import func

from app.extensions import db
from app.models import BodyTypeCategory


def get_by_name(name: str) -> BodyTypeCategory | None:
    """Case-insensitive lookup - the CNN's class labels are lowercase
    (see ai_model/training/model_architecture.py CLASS_NAMES), the
    seeded rows are capitalized ("Thin", "Normal", "Overweight")."""
    return BodyTypeCategory.query.filter(func.lower(BodyTypeCategory.name) == name.lower()).first()


def get_all() -> list[BodyTypeCategory]:
    return BodyTypeCategory.query.order_by(BodyTypeCategory.body_type_id).all()


def get_by_id(body_type_id: int) -> BodyTypeCategory | None:
    return db.session.get(BodyTypeCategory, body_type_id)


def update(body_type: BodyTypeCategory, **kwargs) -> BodyTypeCategory:
    for key, value in kwargs.items():
        setattr(body_type, key, value)
    db.session.commit()
    return body_type
