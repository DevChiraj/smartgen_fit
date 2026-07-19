"""Secure image upload handling: extension, size, and real image-content checks.
Shared by profile pictures (Module 4) and body-analysis photos (Module 10)."""

import os
import uuid

from PIL import Image, UnidentifiedImageError

from app.utils.exceptions import ValidationFailedError


def _allowed_extension(filename: str, allowed_extensions: set) -> str | None:
    if "." not in filename:
        return None
    extension = filename.rsplit(".", 1)[1].lower()
    return extension if extension in allowed_extensions else None


def validate_and_save_image(
    file, upload_folder: str, allowed_extensions: set, max_bytes: int
) -> str:
    """Validate an uploaded FileStorage and persist it, returning the saved filename."""
    if file is None or file.filename == "":
        raise ValidationFailedError("No file was uploaded.")

    extension = _allowed_extension(file.filename, allowed_extensions)
    if extension is None:
        raise ValidationFailedError(
            f"Unsupported file type. Allowed: {', '.join(sorted(allowed_extensions))}."
        )

    file.stream.seek(0, os.SEEK_END)
    size = file.stream.tell()
    file.stream.seek(0)
    if size > max_bytes:
        raise ValidationFailedError(
            f"File too large. Maximum size is {max_bytes // (1024 * 1024)} MB."
        )

    try:
        Image.open(file.stream).verify()
    except (UnidentifiedImageError, OSError):
        raise ValidationFailedError("The uploaded file is not a valid image.")
    file.stream.seek(0)

    os.makedirs(upload_folder, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.{extension}"
    file.save(os.path.join(upload_folder, filename))

    return filename


def delete_profile_picture(upload_folder: str, filename: str | None) -> None:
    if not filename:
        return
    path = os.path.join(upload_folder, filename)
    if os.path.exists(path):
        os.remove(path)
