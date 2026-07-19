"""Loads the preprocessed dataset (datasets/body_images_processed/) into
train/validation arrays for training.

Reads directly from the class-labeled folders build_dataset.py writes
(already resized/denoised/contrast-normalized by opencv_pipeline.py) -
this module only turns them into (X, y) arrays and a stratified
train/val split. It does not read labels.csv; the folder a file lives
in is its label, same convention as the rest of the preprocessing
pipeline.
"""

from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split

from model_architecture import CLASS_NAMES, INPUT_SHAPE


def load_dataset(processed_dir: Path):
    images = []
    labels = []

    for class_index, class_name in enumerate(CLASS_NAMES):
        class_dir = Path(processed_dir) / class_name
        if not class_dir.is_dir():
            continue
        for image_path in sorted(class_dir.iterdir()):
            if not image_path.is_file():
                continue
            with Image.open(image_path) as img:
                img = img.convert("RGB").resize(INPUT_SHAPE[:2])
                images.append(np.asarray(img, dtype=np.float32))
            labels.append(class_index)

    if not images:
        raise ValueError(f"No images found under {processed_dir}")

    return np.stack(images), np.array(labels)


def train_val_split(images, labels, val_ratio=0.2, seed=42):
    """Stratified split keeps each class proportionally represented in
    both sets; falls back to a plain split if a class is too small to
    stratify with the requested ratio."""
    try:
        return train_test_split(
            images, labels, test_size=val_ratio, random_state=seed, stratify=labels
        )
    except ValueError:
        return train_test_split(images, labels, test_size=val_ratio, random_state=seed)
