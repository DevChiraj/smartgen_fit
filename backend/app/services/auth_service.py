"""Registration, authentication, and JWT issuing. No AI/recommendation logic here."""

from flask_jwt_extended import create_access_token, create_refresh_token

from app.extensions import bcrypt
from app.models import User
from app.repositories import user_repository
from app.utils.exceptions import (
    DuplicateResourceError,
    InvalidCredentialsError,
    UnderMinimumAgeError,
)
from app.utils.validators import calculate_age

MIN_REGISTRATION_AGE = 15


def register_user(data: dict) -> User:
    age = calculate_age(data["date_of_birth"])
    if age < MIN_REGISTRATION_AGE:
        raise UnderMinimumAgeError(
            f"You must be at least {MIN_REGISTRATION_AGE} years old to register."
        )

    if user_repository.get_by_email(data["email"]) is not None:
        raise DuplicateResourceError("Email is already registered.")
    if user_repository.get_by_username(data["username"]) is not None:
        raise DuplicateResourceError("Username is already taken.")

    user = User(
        full_name=data["full_name"],
        date_of_birth=data["date_of_birth"],
        age=age,
        gender=data["gender"],
        email=data["email"],
        phone_number=data.get("phone_number"),
        height_cm=data.get("height_cm"),
        weight_kg=data.get("weight_kg"),
        username=data["username"],
        password_hash=bcrypt.generate_password_hash(data["password"]).decode("utf-8"),
        role="user",
    )
    return user_repository.create(user)


def authenticate(identifier: str, password: str) -> User:
    user = user_repository.get_by_email(identifier) or user_repository.get_by_username(identifier)
    if user is None or not bcrypt.check_password_hash(user.password_hash, password):
        raise InvalidCredentialsError("Invalid username/email or password.")
    return user


def generate_tokens(user: User) -> dict:
    identity = str(user.user_id)
    additional_claims = {"username": user.username, "role": user.role}
    return {
        "access_token": create_access_token(identity=identity, additional_claims=additional_claims),
        "refresh_token": create_refresh_token(
            identity=identity, additional_claims=additional_claims
        ),
    }
