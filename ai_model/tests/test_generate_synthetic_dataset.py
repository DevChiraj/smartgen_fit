from generate_synthetic_dataset import generate_class


def test_generate_class_creates_correct_count(tmp_path):
    rows = generate_class("thin", 5, tmp_path, seed=1)
    assert len(rows) == 5
    assert len(list((tmp_path / "thin").glob("*.png"))) == 5


def test_generate_class_rows_marked_synthetic(tmp_path):
    rows = generate_class("thin", 3, tmp_path, seed=1)
    assert all(r["source"] == "synthetic" for r in rows)
    assert all(r["body_type"] == "thin" for r in rows)


def test_generate_class_bmi_within_expected_range(tmp_path):
    rows = generate_class("thin", 5, tmp_path, seed=1)
    for row in rows:
        assert 15.0 <= row["bmi"] <= 19.0
