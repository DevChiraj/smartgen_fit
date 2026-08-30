import pytest

from encoding import build_feature_vector, encode_bmi_category, encode_gender


def test_encode_gender_known_values():
    assert encode_gender("Male") == 0.0
    assert encode_gender("female") == 1.0


def test_encode_gender_unknown_defaults_to_midpoint():
    assert encode_gender("other") == 0.5
    assert encode_gender("") == 0.5


def test_encode_bmi_category_ordinal_ordering():
    assert encode_bmi_category("Thin") < encode_bmi_category("Normal")
    assert encode_bmi_category("Normal") < encode_bmi_category("Overweight")
    assert encode_bmi_category("Overweight") < encode_bmi_category("Obese")


def test_encode_bmi_category_rejects_unknown_label():
    with pytest.raises(ValueError):
        encode_bmi_category("not-a-category")


def test_build_feature_vector_shape():
    vector = build_feature_vector(30, "Male", "Normal")
    assert vector == [30.0, 0.0, 1.0]
