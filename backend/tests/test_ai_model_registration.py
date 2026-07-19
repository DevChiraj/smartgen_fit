import json

import pytest

from app.models import AIModelFile
from app.services.ai_model_registration_service import register_model
from app.utils.exceptions import DuplicateResourceError


def _write_metadata(tmp_path, version="v20260101_000000", accuracy=0.5):
    metadata = {
        "version": version,
        "file_path": f"ai_model/saved_models/{version}.keras",
        "accuracy": accuracy,
        "trained_date": "2026-01-01T00:00:00+00:00",
        "class_names": ["normal", "overweight", "thin"],
        "train_count": 38,
        "val_count": 10,
        "epochs": 15,
    }
    path = tmp_path / f"{version}.json"
    path.write_text(json.dumps(metadata))
    return path


def test_register_model_creates_active_row(db, tmp_path):
    metadata_path = _write_metadata(tmp_path)

    model_file = register_model(metadata_path)

    assert model_file.version == "v20260101_000000"
    assert model_file.is_active is True
    assert AIModelFile.query.count() == 1


def test_register_model_deactivates_previous_active_model(db, tmp_path):
    register_model(_write_metadata(tmp_path, version="v1"))
    register_model(_write_metadata(tmp_path, version="v2"))

    v1 = AIModelFile.query.filter_by(version="v1").first()
    v2 = AIModelFile.query.filter_by(version="v2").first()

    assert v1.is_active is False
    assert v2.is_active is True


def test_register_model_rejects_duplicate_version(db, tmp_path):
    metadata_path = _write_metadata(tmp_path, version="v1")
    register_model(metadata_path)

    with pytest.raises(DuplicateResourceError):
        register_model(metadata_path)
