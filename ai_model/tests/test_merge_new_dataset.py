import csv

import pandas as pd
from PIL import Image

from merge_new_dataset import merge_dataset


def _make_image(path, size=(200, 200)):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size).save(path)


def _make_excel(path, rows):
    pd.DataFrame(rows).to_excel(path, index=False)


def _read_labels(labels_path):
    with open(labels_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_merge_copies_image_and_appends_label_with_real_folder_casing(tmp_path):
    source = tmp_path / "New_dataset"
    _make_image(source / "Thin" / "T1.jpg")
    _make_excel(
        source / "data.xlsx",
        [
            {
                "subject_id": "T1",
                "height_cm": 180,
                "weight_kg": 55,
                "bmi": 17.0,
                "body_type": "Thin",
            }
        ],
    )
    body_images_dir = tmp_path / "body_images"

    result = merge_dataset(source, source / "data.xlsx", body_images_dir, "test_source")

    assert len(result["merged"]) == 1
    dest = body_images_dir / "thin" / "T1.jpg"
    assert dest.is_file()

    rows = _read_labels(body_images_dir / "labels.csv")
    assert len(rows) == 1
    assert rows[0]["subject_id"] == "T1"
    assert rows[0]["body_type"] == "thin"
    assert rows[0]["dataset_source"] == "test_source"
    # Source folder on disk is "Thin" (capitalized) - the recorded path must
    # preserve that real casing, not the lowercase value from the Excel sheet.
    assert "/Thin/" in rows[0]["source_image"]


def test_merge_skips_subject_id_already_in_labels_csv(tmp_path):
    source = tmp_path / "New_dataset"
    _make_image(source / "Normal" / "N1.jpg")
    _make_excel(
        source / "data.xlsx",
        [
            {
                "subject_id": "N1",
                "height_cm": 170,
                "weight_kg": 65,
                "bmi": 22.5,
                "body_type": "Normal",
            }
        ],
    )
    body_images_dir = tmp_path / "body_images"
    body_images_dir.mkdir()
    with open(body_images_dir / "labels.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "subject_id",
                "source_image",
                "dest_image",
                "height_cm",
                "weight_kg",
                "bmi",
                "body_type",
                "dataset_source",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "subject_id": "N1",
                "source_image": "elsewhere.jpg",
                "dest_image": "elsewhere_dest.jpg",
                "height_cm": 170,
                "weight_kg": 65,
                "bmi": 22.5,
                "body_type": "normal",
                "dataset_source": "already_here",
            }
        )

    result = merge_dataset(source, source / "data.xlsx", body_images_dir, "test_source")

    assert result["merged"] == []
    assert result["skipped_collision"] == ["N1"]
    # The pre-existing row must be untouched, not overwritten.
    rows = _read_labels(body_images_dir / "labels.csv")
    assert rows[0]["dataset_source"] == "already_here"


def test_merge_skips_subject_with_no_matching_image_file(tmp_path):
    source = tmp_path / "New_dataset"
    (source / "Overweight").mkdir(parents=True)
    _make_excel(
        source / "data.xlsx",
        [
            {
                "subject_id": "O1",
                "height_cm": 170,
                "weight_kg": 90,
                "bmi": 31.1,
                "body_type": "Overweight",
            }
        ],
    )
    body_images_dir = tmp_path / "body_images"

    result = merge_dataset(source, source / "data.xlsx", body_images_dir, "test_source")

    assert result["merged"] == []
    assert result["skipped_missing_image"] == ["O1"]


def test_merge_flags_bmi_body_type_mismatch_instead_of_merging(tmp_path):
    source = tmp_path / "New_dataset"
    _make_image(source / "Overweight" / "BAD1.jpg")
    # height/weight computes to a Normal-range BMI, but the sheet claims Overweight.
    _make_excel(
        source / "data.xlsx",
        [
            {
                "subject_id": "BAD1",
                "height_cm": 170,
                "weight_kg": 65,
                "bmi": 22.5,
                "body_type": "Overweight",
            }
        ],
    )
    body_images_dir = tmp_path / "body_images"

    result = merge_dataset(source, source / "data.xlsx", body_images_dir, "test_source")

    assert result["merged"] == []
    assert len(result["flagged_bmi_mismatch"]) == 1
    assert not (body_images_dir / "overweight" / "BAD1.jpg").exists()


def test_dry_run_reports_without_writing_anything(tmp_path):
    source = tmp_path / "New_dataset"
    _make_image(source / "Thin" / "T2.jpg")
    _make_excel(
        source / "data.xlsx",
        [
            {
                "subject_id": "T2",
                "height_cm": 180,
                "weight_kg": 55,
                "bmi": 17.0,
                "body_type": "Thin",
            }
        ],
    )
    body_images_dir = tmp_path / "body_images"

    result = merge_dataset(
        source, source / "data.xlsx", body_images_dir, "test_source", dry_run=True
    )

    assert len(result["merged"]) == 1
    assert not (body_images_dir / "labels.csv").exists()
    assert not (body_images_dir / "thin" / "T2.jpg").exists()
