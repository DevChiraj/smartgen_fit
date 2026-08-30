import pytest
from PIL import Image

from opencv_pipeline import (
    crop_to_body,
    denoise_image,
    detect_body_bounding_box,
    load_image,
    normalize_contrast,
    preprocess_and_save,
    preprocess_image,
    resize_image,
)


def _make_test_image(tmp_path, size=(300, 500), color=(180, 140, 120)):
    path = tmp_path / "test.jpg"
    Image.new("RGB", size, color=color).save(path)
    return path


def test_load_image_raises_on_missing_file(tmp_path):
    with pytest.raises(ValueError):
        load_image(tmp_path / "missing.jpg")


def test_resize_image_produces_requested_size(tmp_path):
    image = load_image(_make_test_image(tmp_path))
    resized = resize_image(image, (224, 224))
    assert resized.shape[:2] == (224, 224)


def test_denoise_and_normalize_preserve_shape(tmp_path):
    image = load_image(_make_test_image(tmp_path))
    denoised = denoise_image(image)
    assert denoised.shape == image.shape
    normalized = normalize_contrast(denoised)
    assert normalized.shape == image.shape


def test_detect_body_bounding_box_returns_none_on_blank_image(tmp_path):
    image = load_image(_make_test_image(tmp_path, color=(255, 255, 255)))
    assert detect_body_bounding_box(image) is None


def test_crop_to_body_falls_back_to_full_image_when_no_box(tmp_path):
    image = load_image(_make_test_image(tmp_path))
    cropped = crop_to_body(image, None)
    assert cropped.shape == image.shape


def test_preprocess_image_produces_correct_output_size(tmp_path):
    result, body_detected = preprocess_image(
        _make_test_image(tmp_path), output_size=(128, 128)
    )
    assert result.shape[:2] == (128, 128)
    assert isinstance(body_detected, bool)


def test_preprocess_and_save_writes_file(tmp_path):
    source = _make_test_image(tmp_path)
    dest = tmp_path / "out" / "processed.jpg"
    preprocess_and_save(source, dest, output_size=(64, 64))
    assert dest.exists()
    assert load_image(dest).shape[:2] == (64, 64)
