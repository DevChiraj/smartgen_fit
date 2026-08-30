"""Loads the trained KNN recommender and matches a user to the nearest
Person_ID from the meal/workout dataset.

Loaded directly by the backend's RecommendationService (via
backend/app/ml_recommendation.py) - this is the only other place ai_model/
code runs inside a live request besides predict.py. Takes the CNN's
predicted body type label plus the user's age/gender and returns a
Person_ID; it has no knowledge of what meal/workout content that ID maps
to (recommendation_service.py fetches that from the DB). Same
train/inference-must-match principle as predict.py + opencv_pipeline.py:
encoding.py is imported by both train_recommender.py and this module so
the query vector is built the same way the training vectors were.
"""

import json
import sys
from pathlib import Path

_RECOMMENDATION_DIR = Path(__file__).resolve().parent
if str(_RECOMMENDATION_DIR) not in sys.path:
    sys.path.insert(0, str(_RECOMMENDATION_DIR))

import joblib  # noqa: E402

from encoding import build_feature_vector  # noqa: E402

_REPO_ROOT = _RECOMMENDATION_DIR.parent.parent
_DEFAULT_ACTIVE_POINTER = (
    _RECOMMENDATION_DIR.parent / "saved_models" / "recommender_active.json"
)

_bundle_cache: dict[str, dict] = {}


def _resolve_active_bundle_path() -> str:
    pointer = json.loads(_DEFAULT_ACTIVE_POINTER.read_text())
    return str(_REPO_ROOT / pointer["file_path"])


def _load_bundle(bundle_path: str) -> dict:
    if bundle_path not in _bundle_cache:
        _bundle_cache[bundle_path] = joblib.load(bundle_path)
    return _bundle_cache[bundle_path]


def find_matching_person(
    body_type_label: str, age: int, gender: str, bundle_path: str | None = None
) -> str:
    """Returns the Person_ID of the nearest-neighbor candidate record."""
    resolved_path = bundle_path or _resolve_active_bundle_path()
    bundle = _load_bundle(resolved_path)

    query = [build_feature_vector(age, gender, body_type_label)]
    scaled_query = bundle["scaler"].transform(query)

    _distances, indices = bundle["knn"].kneighbors(scaled_query, n_neighbors=1)
    nearest_index = int(indices[0][0])
    return bundle["person_ids"][nearest_index]
