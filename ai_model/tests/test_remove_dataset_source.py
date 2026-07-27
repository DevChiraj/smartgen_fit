import csv

from PIL import Image

from remove_dataset_source import remove_dataset_source

FIELDNAMES = [
    "subject_id",
    "source_image",
    "dest_image",
    "height_cm",
    "weight_kg",
    "bmi",
    "body_type",
    "dataset_source",
]


def _write_labels(labels_path, rows):
    with open(labels_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def _make_image(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (200, 200)).save(path)


def _setup(body_images_dir):
    _make_image(body_images_dir / "thin" / "ds3_2_front_img.png")
    # A real gotcha: ds3_2 is a string-prefix of ds3_20 - must not delete it too.
    _make_image(body_images_dir / "thin" / "ds3_20_front_img.png")
    _make_image(body_images_dir / "normal" / "hf_0_front_img.jpg")

    _write_labels(
        body_images_dir / "labels.csv",
        [
            {
                "subject_id": "ds3_2",
                "source_image": "raw_dataset/dataset3/2.png",
                "dest_image": "datasets/body_images\\thin\\ds3_2_front_img.png",
                "height_cm": 185,
                "weight_kg": 52,
                "bmi": 15.19,
                "body_type": "thin",
                "dataset_source": "dataset_3",
            },
            {
                "subject_id": "ds3_20",
                "source_image": "raw_dataset/dataset3/20.png",
                "dest_image": "datasets/body_images\\thin\\ds3_20_front_img.png",
                "height_cm": 173,
                "weight_kg": 80,
                "bmi": 26.73,
                "body_type": "thin",
                "dataset_source": "dataset_3",
            },
            {
                "subject_id": "hf_0",
                "source_image": "raw_dataset/files/0/front_img.jpg",
                "dest_image": "datasets/body_images\\normal\\hf_0_front_img.jpg",
                "height_cm": 159,
                "weight_kg": 49,
                "bmi": 19.38,
                "body_type": "normal",
                "dataset_source": "hugging_face",
            },
        ],
    )


def test_removes_only_matching_rows_and_files_not_prefix_collisions(tmp_path):
    body_images_dir = tmp_path / "body_images"
    _setup(body_images_dir)

    result = remove_dataset_source(body_images_dir, "dataset_3")

    assert {r["subject_id"] for r in result["removed"]} == {"ds3_2", "ds3_20"}
    assert not (body_images_dir / "thin" / "ds3_2_front_img.png").exists()
    assert not (body_images_dir / "thin" / "ds3_20_front_img.png").exists()
    # hf_0 belongs to a different dataset_source - must survive untouched.
    assert (body_images_dir / "normal" / "hf_0_front_img.jpg").exists()

    rows = list(
        csv.DictReader(
            open(body_images_dir / "labels.csv", newline="", encoding="utf-8")
        )
    )
    assert {r["subject_id"] for r in rows} == {"hf_0"}


def test_dry_run_reports_without_deleting_anything(tmp_path):
    body_images_dir = tmp_path / "body_images"
    _setup(body_images_dir)

    result = remove_dataset_source(body_images_dir, "dataset_3", dry_run=True)

    assert len(result["removed"]) == 2
    assert (body_images_dir / "thin" / "ds3_2_front_img.png").exists()
    assert (body_images_dir / "thin" / "ds3_20_front_img.png").exists()
    rows = list(
        csv.DictReader(
            open(body_images_dir / "labels.csv", newline="", encoding="utf-8")
        )
    )
    assert len(rows) == 3


def test_unknown_dataset_source_removes_nothing(tmp_path):
    body_images_dir = tmp_path / "body_images"
    _setup(body_images_dir)

    result = remove_dataset_source(body_images_dir, "no_such_source")

    assert result["removed"] == []
    assert len(result["kept"]) == 3
