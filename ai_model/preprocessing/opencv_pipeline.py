"""OpenCV preprocessing pipeline: resize, crop, normalize.

Implements the "Preprocessing" + "OpenCV Processing" + "Body Detection"
stages of the AI workflow in SYSTEM.md section 6 - everything up to
(but not including) CNN feature extraction/classification, which is
Module 9's job. This module never touches meal/workout data and knows
nothing about the CNN; it only turns a raw photo into a clean, fixed-
size array ready to hand to a model.

Pipeline: load -> detect + crop to the body region (HOG person
detector, falls back to the full frame if nothing is detected, which
happens often on tightly-cropped close-up photos) -> denoise ->
CLAHE contrast normalization -> resize to a fixed size.
"""

from pathlib import Path

import cv2
import numpy as np

DEFAULT_OUTPUT_SIZE = (224, 224)

_hog = cv2.HOGDescriptor()
_hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())


def load_image(path) -> np.ndarray:
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError(f"Could not read image: {path}")
    return image


def detect_body_bounding_box(image: np.ndarray):
    """Returns (x, y, w, h) for the largest detected person, or None."""
    detect_input = image
    scale = 1.0
    max_dim = 640
    longest_side = max(image.shape[:2])
    if longest_side > max_dim:
        scale = max_dim / longest_side
        detect_input = cv2.resize(image, None, fx=scale, fy=scale)

    boxes, weights = _hog.detectMultiScale(
        detect_input, winStride=(8, 8), padding=(16, 16), scale=1.05
    )
    if len(boxes) == 0:
        return None

    best_index = int(np.argmax(weights))
    x, y, w, h = boxes[best_index]
    if scale != 1.0:
        x, y, w, h = (int(v / scale) for v in (x, y, w, h))
    return (x, y, w, h)


def crop_to_body(image: np.ndarray, box, padding_ratio: float = 0.15) -> np.ndarray:
    """Crops to the given (x, y, w, h) box with padding, clamped to the frame.
    Falls back to the full image when box is None (no person detected)."""
    height, width = image.shape[:2]
    if box is None:
        return image

    x, y, w, h = box
    pad_x = int(w * padding_ratio)
    pad_y = int(h * padding_ratio)
    x0 = max(0, x - pad_x)
    y0 = max(0, y - pad_y)
    x1 = min(width, x + w + pad_x)
    y1 = min(height, y + h + pad_y)
    if x1 <= x0 or y1 <= y0:
        return image
    return image[y0:y1, x0:x1]


def denoise_image(image: np.ndarray) -> np.ndarray:
    return cv2.bilateralFilter(image, d=7, sigmaColor=50, sigmaSpace=50)


def normalize_contrast(image: np.ndarray) -> np.ndarray:
    """CLAHE (adaptive histogram equalization) on the lightness channel only,
    so contrast/lighting is normalized without distorting color."""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_channel = clahe.apply(l_channel)
    lab = cv2.merge((l_channel, a_channel, b_channel))
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def resize_image(image: np.ndarray, size=DEFAULT_OUTPUT_SIZE) -> np.ndarray:
    return cv2.resize(image, size, interpolation=cv2.INTER_AREA)


def preprocess_image(path, output_size=DEFAULT_OUTPUT_SIZE):
    """Runs the full pipeline on one image file, returns (array, body_detected)."""
    image = load_image(path)
    box = detect_body_bounding_box(image)
    image = crop_to_body(image, box)
    image = denoise_image(image)
    image = normalize_contrast(image)
    image = resize_image(image, output_size)
    return image, box is not None


def preprocess_and_save(source_path, dest_path, output_size=DEFAULT_OUTPUT_SIZE):
    image, body_detected = preprocess_image(source_path, output_size)
    Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(dest_path), image)
    return body_detected
