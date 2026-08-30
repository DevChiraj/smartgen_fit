from label_dataset_by_bmi import classify_bmi, find_companion_image, to_cm, to_kg


def test_classify_bmi_thin():
    assert classify_bmi(17.9) == "thin"


def test_classify_bmi_boundary_thin_to_normal():
    assert classify_bmi(18.5) == "normal"


def test_classify_bmi_boundary_normal_to_overweight():
    assert classify_bmi(25.0) == "overweight"


def test_classify_bmi_overweight():
    assert classify_bmi(30.0) == "overweight"


def test_to_cm_conversions():
    assert to_cm("170", "cm") == 170.0
    assert to_cm("1.7", "m") == 170.0
    assert to_cm("66.9", "in") == 66.9 * 2.54


def test_to_kg_conversions():
    assert to_kg("70", "kg") == 70.0
    assert to_kg("154", "lb") == 154 * 0.453592


def test_find_companion_image_prefers_front(tmp_path):
    (tmp_path / "selfie_img.jpg").write_bytes(b"x")
    (tmp_path / "side_img.jpg").write_bytes(b"x")
    (tmp_path / "front_img.jpg").write_bytes(b"x")

    result = find_companion_image(tmp_path)
    assert result.name == "front_img.jpg"


def test_find_companion_image_returns_none_when_empty(tmp_path):
    assert find_companion_image(tmp_path) is None
