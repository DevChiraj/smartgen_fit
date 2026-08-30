"""Registers a trained model (Module 9's train.py output) into the
ai_model_files table. Reads only the metadata JSON sidecar the
training script already wrote - never touches ai_model/ code and
never trains anything itself, keeping the AI pipeline and backend
decoupled per the project's non-negotiable rule 1.
"""

import json
from datetime import datetime
from pathlib import Path

from app.models import AIModelFile
from app.repositories import ai_model_file_repository
from app.utils.exceptions import DuplicateResourceError


def register_model(metadata_path: Path) -> AIModelFile:
    metadata = json.loads(Path(metadata_path).read_text())

    if ai_model_file_repository.get_by_version(metadata["version"]) is not None:
        raise DuplicateResourceError(f"Model version {metadata['version']} is already registered.")

    ai_model_file_repository.deactivate_all()
    return ai_model_file_repository.create(
        version=metadata["version"],
        file_path=metadata["file_path"],
        accuracy=metadata.get("accuracy"),
        trained_date=datetime.fromisoformat(metadata["trained_date"]),
        is_active=True,
    )
