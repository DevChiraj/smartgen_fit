"""DB access for the trained-model registry."""

from app.extensions import db
from app.models import AIModelFile


def get_by_version(version: str) -> AIModelFile | None:
    return AIModelFile.query.filter_by(version=version).first()


def get_active() -> AIModelFile | None:
    return AIModelFile.query.filter_by(is_active=True).first()


def deactivate_all() -> None:
    AIModelFile.query.update({AIModelFile.is_active: False})


def create(**kwargs) -> AIModelFile:
    model_file = AIModelFile(**kwargs)
    db.session.add(model_file)
    db.session.commit()
    return model_file
