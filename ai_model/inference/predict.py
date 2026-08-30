"""Loads a trained model and classifies a single body image.

Loaded directly by the backend's ImageAnalysisService (via
backend/app/ai_inference.py) - this is the only place ai_model/ code
runs inside a live request. Returns a label and confidence score
only; it has no knowledge of meal/workout plans or the database
(rule 1: AI classifies, RecommendationService decides what to
recommend - Module 11).

Reuses the exact same OpenCV preprocessing functions used to build the
training set (opencv_pipeline.py), not a reimplementation - train/
inference preprocessing must match or the model sees a different
input distribution than it learned on.
"""

import sys
from pathlib import Path

_AI_MODEL_DIR = Path(__file__).resolve().parent.parent
for _subdir in ("preprocessing", "training"):
    _path = str(_AI_MODEL_DIR / _subdir)
    if _path not in sys.path:
        sys.path.insert(0, _path)

import numpy as np  # noqa: E402
from tensorflow import keras  # noqa: E402

from model_architecture import CLASS_NAMES, INPUT_SHAPE  # noqa: E402
from opencv_pipeline import (  # noqa: E402
    crop_to_body,
    denoise_image,
    detect_body_bounding_box,
    load_image,
    normalize_contrast,
    resize_image,
)

_model_cache: dict[str, "keras.Model"] = {}


def _load_model(model_path: str):
    if model_path not in _model_cache:
        _model_cache[model_path] = keras.models.load_model(model_path)
    return _model_cache[model_path]


def predict_body_type(image_path: str, model_path: str) -> tuple[str, float]:
    """Runs the training-time preprocessing pipeline, then classifies.

    Returns (label, confidence) where label is one of CLASS_NAMES and
    confidence is the winning class's softmax probability (0-1).
    """
    image = load_image(image_path)
    box = detect_body_bounding_box(image)
    image = crop_to_body(image, box)
    image = denoise_image(image)
    image = normalize_contrast(image)
    image = resize_image(image, INPUT_SHAPE[:2])

    batch = np.expand_dims(image.astype("float32"), axis=0)
    model = _load_model(model_path)
    probabilities = model.predict(batch, verbose=0)[0]

    predicted_index = int(np.argmax(probabilities))
    label = CLASS_NAMES[predicted_index]
    confidence = float(probabilities[predicted_index])
    return label, confidence
