from PIL import Image

from dataset_validator import validate_dataset, validate_image


def test_validate_image_accepts_valid_jpg(tmp_path):
    path = tmp_path / "ok.jpg"
    Image.new("RGB", (200, 200)).save(path)
    assert validate_image(path) is None


def test_validate_image_rejects_unsupported_extension(tmp_path):
    path = tmp_path / "ok.gif"
    Image.new("RGB", (200, 200)).save(path, format="GIF")
    assert "unsupported extension" in validate_image(path)


def test_validate_image_rejects_too_small(tmp_path):
    path = tmp_path / "small.jpg"
    Image.new("RGB", (50, 50)).save(path)
    assert "too small" in validate_image(path)


def test_validate_image_rejects_corrupt_file(tmp_path):
    path = tmp_path / "corrupt.jpg"
    path.write_bytes(b"not an image")
    assert "not a valid" in validate_image(path)


def test_validate_dataset_counts_by_class_and_flags_problems(tmp_path):
    for cls in ("thin", "normal"):
        (tmp_path / cls).mkdir()
    Image.new("RGB", (200, 200)).save(tmp_path / "thin" / "a.jpg")
    Image.new("RGB", (200, 200)).save(tmp_path / "normal" / "b.jpg")
    (tmp_path / "normal" / "bad.jpg").write_bytes(b"garbage")

    counts, problems = validate_dataset(tmp_path)
    assert counts == {"thin": 1, "normal": 1}
    assert len(problems) == 1
