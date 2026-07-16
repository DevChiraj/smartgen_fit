"""Profile view/edit and profile-picture upload business logic."""

import os

from flask import current_app

from app.models import User
from app.repositories import user_repository
from app.utils.file_handler import delete_profile_picture, validate_and_save_profile_picture

PROFILE_PICTURE_URL_PREFIX = "/api/v1/users/uploads/profile-pictures"


def get_profile(user_id: int) -> User:
    return user_repository.get_by_id(user_id)


def update_profile(user_id: int, data: dict) -> User:
    user = user_repository.get_by_id(user_id)
    for field in ("full_name", "phone_number", "height_cm", "weight_kg"):
        if field in data:
            setattr(user, field, data[field])
    return user_repository.save(user)


def update_profile_picture(user_id: int, file) -> User:
    user = user_repository.get_by_id(user_id)
    upload_folder = current_app.config["UPLOAD_FOLDER"]

    filename = validate_and_save_profile_picture(
        file,
        upload_folder=upload_folder,
        allowed_extensions=current_app.config["PROFILE_PICTURE_ALLOWED_EXTENSIONS"],
        max_bytes=current_app.config["PROFILE_PICTURE_MAX_BYTES"],
    )

    old_filename = os.path.basename(user.profile_picture_url) if user.profile_picture_url else None
    user.profile_picture_url = f"{PROFILE_PICTURE_URL_PREFIX}/{filename}"
    user_repository.save(user)

    delete_profile_picture(upload_folder, old_filename)
    return user
