"""Merges a new labeled image dataset into the project's dataset tracking
system (datasets/body_images/labels.csv + datasets/body_images/<class>/),
the same store label_dataset_by_bmi.py, generate_synthetic_dataset.py, and
augment_dataset.py all write to.

Expects --source to contain class-labeled subfolders (Thin/Normal/
Overweight, case-insensitive) and --excel to be a spreadsheet with columns
subject_id, height_cm, weight_kg, bmi, body_type - one row per image,
matched by subject_id == image filename stem.

Non-destructive: only ever copies from --source, never moves or edits it.
Every new image is validated (dataset_validator.py) before copying, and
any subject_id that already exists in labels.csv is skipped and reported,
never silently overwritten - collisions need a human decision, not a
guess. Recomputes each row's BMI from height/weight and cross-checks both
the recorded BMI and the body_type label against it, flagging (not
silently accepting) anything that doesn't line up - the same kind of
check that caught dataset_3's fabricated weight column in Module 9.

Does NOT run the OpenCV preprocessing step - after merging, run
build_dataset.py so the new images actually reach
datasets/body_images_processed/, which is what train.py/finetune.py read
from. See datasets/datasets_README.md.

USAGE
-----
    python merge_new_dataset.py --source ../../New_dataset \
        --excel ../../New_dataset/Body_Measurement_details.xlsx \
        --dataset-source new_dataset_2026
"""

import argparse
import csv
import shutil
from pathlib import Path

import pandas as pd

from dataset_validator import validate_image

LABEL_FIELDNAMES = [
    "subject_id",
    "source_image",
    "dest_image",
    "height_cm",
    "weight_kg",
    "bmi",
    "body_type",
    "dataset_source",
]
BMI_TOLERANCE = 0.5


def _expected_category(bmi: float) -> str:
    if bmi < 18.5:
        return "thin"
    if bmi < 25:
        return "normal"
    return "overweight"


def _read_labels(labels_path: Path):
    if not labels_path.exists():
        return []
    with open(labels_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_labels(labels_path: Path, rows):
    with open(labels_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LABEL_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def _find_source_image(source: Path, body_type: str, subject_id: str):
    """Matches the class subfolder case-insensitively (Thin/Normal/
    Overweight vs thin/normal/overweight) but returns a path built from
    the real on-disk directory name. Windows resolves either casing to
    the same folder, which would otherwise let a wrong-cased path get
    recorded in labels.csv and silently fail on a case-sensitive
    filesystem (Linux CI, containers) later."""
    if not source.is_dir():
        return None
    for class_dir in source.iterdir():
        if class_dir.is_dir() and class_dir.name.lower() == body_type.lower():
            matches = sorted(class_dir.glob(f"{subject_id}.*"))
            if matches:
                return matches[0]
    return None


def merge_dataset(
    source: Path,
    excel_path: Path,
    body_images_dir: Path,
    dataset_source_tag: str,
    dry_run: bool = False,
):
    df = pd.read_excel(excel_path)
    required_columns = {"subject_id", "height_cm", "weight_kg", "bmi", "body_type"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Excel file is missing required columns: {missing_columns}")

    labels_path = body_images_dir / "labels.csv"
    existing_rows = _read_labels(labels_path)
    existing_ids = {row["subject_id"] for row in existing_rows}

    merged, skipped_collision, skipped_missing_image = [], [], []
    skipped_invalid_image, flagged_bmi_mismatch = [], []

    for _, row in df.iterrows():
        subject_id = str(row["subject_id"]).strip()
        body_type = str(row["body_type"]).strip().lower()
        height_cm = float(row["height_cm"])
        weight_kg = float(row["weight_kg"])
        recorded_bmi = float(row["bmi"])

        if subject_id in existing_ids:
            skipped_collision.append(subject_id)
            continue

        source_image = _find_source_image(source, body_type, subject_id)
        if source_image is None:
            skipped_missing_image.append(subject_id)
            continue

        reason = validate_image(source_image)
        if reason:
            skipped_invalid_image.append((subject_id, reason))
            continue

        computed_bmi = weight_kg / ((height_cm / 100) ** 2)
        expected_type = _expected_category(computed_bmi)
        if (
            abs(computed_bmi - recorded_bmi) > BMI_TOLERANCE
            or expected_type != body_type
        ):
            flagged_bmi_mismatch.append(
                (
                    subject_id,
                    height_cm,
                    weight_kg,
                    recorded_bmi,
                    body_type,
                    computed_bmi,
                )
            )
            continue

        dest_dir = body_images_dir / body_type
        dest_path = dest_dir / f"{subject_id}{source_image.suffix.lower()}"

        if not dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_image, dest_path)

        merged.append(
            {
                "subject_id": subject_id,
                "source_image": source_image.as_posix(),
                "dest_image": dest_path.as_posix(),
                "height_cm": height_cm,
                "weight_kg": weight_kg,
                "bmi": recorded_bmi,
                "body_type": body_type,
                "dataset_source": dataset_source_tag,
            }
        )
        existing_ids.add(subject_id)

    if merged and not dry_run:
        _write_labels(labels_path, existing_rows + merged)

    print(f"Merged: {len(merged)}")
    counts = {}
    for row in merged:
        counts[row["body_type"]] = counts.get(row["body_type"], 0) + 1
    print(f"  Per-class: {counts}")

    if skipped_collision:
        print(f"\nSkipped (subject_id already in labels.csv): {len(skipped_collision)}")
        print(f"  {skipped_collision}")
    if skipped_missing_image:
        print(f"\nSkipped (no matching image file found): {len(skipped_missing_image)}")
        print(f"  {skipped_missing_image}")
    if skipped_invalid_image:
        print(f"\nSkipped (image failed validation): {len(skipped_invalid_image)}")
        for subject_id, reason in skipped_invalid_image:
            print(f"  - {subject_id}: {reason}")
    if flagged_bmi_mismatch:
        print(
            f"\nFlagged, NOT merged (recorded BMI/body_type disagrees with "
            f"height/weight by more than {BMI_TOLERANCE}): {len(flagged_bmi_mismatch)}"
        )
        for subject_id, h, w, bmi, bt, computed in flagged_bmi_mismatch:
            print(
                f"  - {subject_id}: height={h}cm weight={w}kg recorded_bmi={bmi} "
                f"body_type={bt} computed_bmi={computed:.2f}"
            )

    if dry_run:
        print("\nDRY RUN - no files copied, labels.csv not modified.")
    elif merged:
        print(f"\nlabels.csv updated: {labels_path}")
        print(
            "\nNEXT STEP: re-run the OpenCV preprocessing pipeline so these new "
            "images reach datasets/body_images_processed/ (train.py/finetune.py "
            "read from there, not from body_images/ directly):\n"
            "  cd ../../ai_model/preprocessing\n"
            "  python build_dataset.py --source ../../datasets/body_images "
            "--out ../../datasets/body_images_processed"
        )

    return {
        "merged": merged,
        "skipped_collision": skipped_collision,
        "skipped_missing_image": skipped_missing_image,
        "skipped_invalid_image": skipped_invalid_image,
        "flagged_bmi_mismatch": flagged_bmi_mismatch,
    }


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--excel", type=Path, required=True)
    parser.add_argument(
        "--body-images-dir", type=Path, default=Path("../../datasets/body_images")
    )
    parser.add_argument("--dataset-source", type=str, default="new_dataset_2026")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would happen without writing anything",
    )
    args = parser.parse_args()

    merge_dataset(
        source=args.source,
        excel_path=args.excel,
        body_images_dir=args.body_images_dir,
        dataset_source_tag=args.dataset_source,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
