"""Upload -> validate -> preprocess -> classify -> store. No meal/workout
data touched here - this service returns a body-type label and
confidence only, matching rule 1. Populating user_recommendations from
a classification is RecommendationService's job (Module 11).
"""

import os

from flask import current_app

from app.ai_inference import classify_body_image
from app.config import PROJECT_ROOT
from app.models import ImageAnalysisRecord
from app.repositories import (
    ai_model_file_repository,
    body_type_repository,
    image_analysis_repository,
)
from app.utils.exceptions import AppError
from app.utils.file_handler import validate_and_save_image

IMAGE_URL_PREFIX = "/api/v1/image-analysis/uploads"


class NoActiveModelError(AppError):
    status_code = 503


def analyze(user_id: int, file) -> ImageAnalysisRecord:
    active_model = ai_model_file_repository.get_active()
    if active_model is None:
        raise NoActiveModelError(
            "No trained model is currently registered. Run Module 9's training "
            "pipeline and `flask register-model` before analyzing images."
        )

    upload_folder = current_app.config["BODY_IMAGE_UPLOAD_FOLDER"]
    filename = validate_and_save_image(
        file,
        upload_folder=upload_folder,
        allowed_extensions=current_app.config["BODY_IMAGE_ALLOWED_EXTENSIONS"],
        max_bytes=current_app.config["BODY_IMAGE_MAX_BYTES"],
    )

    image_abs_path = os.path.join(upload_folder, filename)
    model_abs_path = os.path.join(PROJECT_ROOT, active_model.file_path)

    label, confidence = classify_body_image(image_abs_path, model_abs_path)

    body_type = body_type_repository.get_by_name(label)
    if body_type is None:
        raise AppError(
            f"Model predicted body type '{label}', which has no matching "
            "body_type_categories row.",
            status_code=500,
        )

    return image_analysis_repository.create(
        user_id=user_id,
        image_path=f"{IMAGE_URL_PREFIX}/{filename}",
        predicted_body_type_id=body_type.body_type_id,
        confidence_score=confidence,
    )


def get_history(user_id: int) -> list[ImageAnalysisRecord]:
    return image_analysis_repository.get_history_for_user(user_id)
