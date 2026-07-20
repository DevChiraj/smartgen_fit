"""Admin-only body type category management. Update (description) only -
see admin_schema.py's BodyTypeUpdateSchema for why `name` is not editable
and no create/delete is offered: the set is architecturally fixed to
match ai_model's CLASS_NAMES (Thin/Normal/Overweight).
"""

from app.models import BodyTypeCategory
from app.repositories import body_type_repository
from app.utils.exceptions import NotFoundError


def list_body_types() -> list[BodyTypeCategory]:
    return body_type_repository.get_all()


def get_body_type(body_type_id: int) -> BodyTypeCategory:
    body_type = body_type_repository.get_by_id(body_type_id)
    if body_type is None:
        raise NotFoundError(f"No body type found with id {body_type_id}.")
    return body_type


def update_body_type(body_type_id: int, data: dict) -> BodyTypeCategory:
    body_type = get_body_type(body_type_id)
    return body_type_repository.update(body_type, **data)
