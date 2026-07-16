"""Request/response orchestration for profile endpoints."""

from app.schemas.user_schema import UserPublicSchema, UserUpdateSchema
from app.services import user_service

user_schema = UserPublicSchema()
user_update_schema = UserUpdateSchema()


def handle_get_me(user_id: str):
    user = user_service.get_profile(int(user_id))
    return {"user": user_schema.dump(user)}, 200


def handle_update_me(user_id: str, json_body):
    data = user_update_schema.load(json_body or {}, partial=True)
    user = user_service.update_profile(int(user_id), data)
    return {"user": user_schema.dump(user)}, 200


def handle_upload_profile_picture(user_id: str, file):
    user = user_service.update_profile_picture(int(user_id), file)
    return {"user": user_schema.dump(user)}, 200
