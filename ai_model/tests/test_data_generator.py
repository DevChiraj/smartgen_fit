import numpy as np
import pytest
from PIL import Image

from data_generator import load_dataset, train_val_split
from model_architecture import CLASS_NAMES, INPUT_SHAPE


def _make_class_images(tmp_path, counts):
    """counts: dict of class_name -> number of images to create."""
    for class_name, count in counts.items():
        class_dir = tmp_path / class_name
        class_dir.mkdir()
        for i in range(count):
            Image.new("RGB", (50, 80), color=(i * 10 % 255, 100, 150)).save(
                class_dir / f"{i}.png"
            )


def test_load_dataset_reads_all_images_with_correct_labels(tmp_path):
    _make_class_images(tmp_path, {"normal": 3, "overweight": 2, "thin": 1})

    images, labels = load_dataset(tmp_path)

    assert images.shape == (6, INPUT_SHAPE[0], INPUT_SHAPE[1], 3)
    assert len(labels) == 6
    assert list(labels).count(CLASS_NAMES.index("normal")) == 3
    assert list(labels).count(CLASS_NAMES.index("overweight")) == 2
    assert list(labels).count(CLASS_NAMES.index("thin")) == 1


def test_load_dataset_raises_on_empty_directory(tmp_path):
    with pytest.raises(ValueError):
        load_dataset(tmp_path)


def test_train_val_split_preserves_total_count(tmp_path):
    _make_class_images(tmp_path, {"normal": 6, "overweight": 6, "thin": 6})
    images, labels = load_dataset(tmp_path)

    x_train, x_val, y_train, y_val = train_val_split(
        images, labels, val_ratio=0.25, seed=1
    )

    assert len(x_train) + len(x_val) == len(images)
    assert len(y_train) + len(y_val) == len(labels)


def test_train_val_split_is_deterministic_with_same_seed(tmp_path):
    _make_class_images(tmp_path, {"normal": 6, "overweight": 6, "thin": 6})
    images, labels = load_dataset(tmp_path)

    split_a = train_val_split(images, labels, seed=7)
    split_b = train_val_split(images, labels, seed=7)

    assert np.array_equal(split_a[2], split_b[2])  # y_train matches
