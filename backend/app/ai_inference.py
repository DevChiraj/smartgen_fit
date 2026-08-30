"""Thin bridge into ai_model/inference/predict.py - the only place
backend code imports ai_model/ code. Kept as a single narrow function
so tests can mock this instead of loading the real TensorFlow model
(see backend/tests/test_image_analysis.py).
"""

import sys
from pathlib import Path

from app.config import PROJECT_ROOT

_INFERENCE_DIR = Path(PROJECT_ROOT) / "ai_model" / "inference"
if str(_INFERENCE_DIR) not in sys.path:
    sys.path.insert(0, str(_INFERENCE_DIR))


def classify_body_image(image_path: str, model_path: str) -> tuple[str, float]:
    from predict import predict_body_type  # deferred: don't load TensorFlow until needed

    return predict_body_type(image_path, model_path)
