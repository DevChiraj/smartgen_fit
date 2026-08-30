"""Thin bridge into ai_model/recommendation/recommend.py - the second (and
only other) place backend code imports ai_model/ code, alongside
ai_inference.py. Kept as a single narrow function so tests can mock this
instead of loading the real joblib bundle (see
backend/tests/test_recommendations.py).
"""

import sys
from pathlib import Path

from app.config import PROJECT_ROOT

_RECOMMENDATION_DIR = Path(PROJECT_ROOT) / "ai_model" / "recommendation"
if str(_RECOMMENDATION_DIR) not in sys.path:
    sys.path.insert(0, str(_RECOMMENDATION_DIR))


def find_matching_person(body_type_label: str, age: int, gender: str) -> str:
    from recommend import (
        find_matching_person as _find_matching_person,
    )  # deferred: don't load joblib until needed

    return _find_matching_person(body_type_label, age, gender)
