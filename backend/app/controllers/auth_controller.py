"""Request/response orchestration for auth endpoints."""

from app.repositories import user_repository
from app.schemas.auth_schema import LoginSchema, RegisterSchema, UserPublicSchema
from app.services import auth_service

register_schema = RegisterSchema()
login_schema = LoginSchema()
user_schema = UserPublicSchema()


def handle_register(json_body):
    data = register_schema.load(json_body or {})
    user = auth_service.register_user(data)
    tokens = auth_service.generate_tokens(user)
    return {"user": user_schema.dump(user), **tokens}, 201


def handle_login(json_body):
    data = login_schema.load(json_body or {})
    user = auth_service.authenticate(data["identifier"], data["password"])
    tokens = auth_service.generate_tokens(user)
    return {"user": user_schema.dump(user), **tokens}, 200


def handle_refresh(user_id: str):
    user = user_repository.get_by_id(int(user_id))
    tokens = auth_service.generate_tokens(user)
    return {"access_token": tokens["access_token"]}, 200


def handle_me(user_id: str):
    user = user_repository.get_by_id(int(user_id))
    return {"user": user_schema.dump(user)}, 200
