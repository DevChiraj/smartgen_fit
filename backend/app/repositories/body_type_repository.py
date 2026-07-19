"""DB access for body type categories."""

from sqlalchemy import func

from app.models import BodyTypeCategory


def get_by_name(name: str) -> BodyTypeCategory | None:
    """Case-insensitive lookup - the CNN's class labels are lowercase
    (see ai_model/training/model_architecture.py CLASS_NAMES), the
    seeded rows are capitalized ("Thin", "Normal", "Overweight")."""
    return BodyTypeCategory.query.filter(func.lower(BodyTypeCategory.name) == name.lower()).first()
