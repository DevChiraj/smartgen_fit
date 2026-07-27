"""Removes every row (and its image file) tagged with a given
`dataset_source` from datasets/body_images/labels.csv - the inverse of
merge_new_dataset.py's job of adding a source in.

Built for the dataset_3 removal (Module 9's documented fabricated
weight_kg column - see documentation/module_reports/module9.md and
datasets/datasets_README.md), but works for any dataset_source tag, so
it's reusable rather than a one-off script.

Locates each image by globbing datasets/body_images/<class>/ for the
subject_id, rather than trusting the row's own dest_image string -
different scripts have recorded that column relative to different
anchors (repo root vs. wherever the script was run from), so resolving
it naively can silently miss the real file or point elsewhere. Globbing
only ever happens inside --body-images-dir/<class>/, so nothing outside
that tree can be touched. Rows for every other dataset_source are left
completely untouched.

Does NOT regenerate datasets/body_images_processed/ - that directory can
contain stale processed copies of removed images, so delete and rebuild
it afterward:

    rm -rf datasets/body_images_processed
    python build_dataset.py --source ../../datasets/body_images \
        --out ../../datasets/body_images_processed

USAGE
-----
    python remove_dataset_source.py --dataset-source dataset_3
"""

import argparse
import csv
from pathlib import Path

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


def _read_labels(labels_path: Path):
    with open(labels_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_labels(labels_path: Path, rows):
    with open(labels_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LABEL_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def _find_dest_image(body_images_dir: Path, body_type: str, subject_id: str):
    """Locates the actual file by globbing datasets/body_images/<class>/,
    not by trusting the recorded dest_image string - different scripts
    have written that column relative to different anchors (repo root vs.
    wherever the script was invoked from), so resolving it naively can
    silently point at the wrong place.

    Matches a filename whose stem is exactly `subject_id`, or starts with
    `subject_id + "_"` (the "<id>_front_img.ext" convention older rows
    use). A bare `subject_id*` glob would also wrongly match e.g.
    "ds3_20_front_img.png" when looking for "ds3_2" - the "_" and "."
    checks rule that out."""
    class_dir = body_images_dir / body_type
    if not class_dir.is_dir():
        return None
    candidates = [
        p for p in class_dir.iterdir() if p.is_file() and p.stem == subject_id
    ]
    candidates += [
        p
        for p in class_dir.iterdir()
        if p.is_file() and p.stem.startswith(f"{subject_id}_")
    ]
    return candidates[0] if candidates else None


def remove_dataset_source(
    body_images_dir: Path, dataset_source: str, dry_run: bool = False
):
    labels_path = body_images_dir / "labels.csv"
    rows = _read_labels(labels_path)

    kept, removed, deleted_files, missing_files = [], [], [], []

    for row in rows:
        if row["dataset_source"] != dataset_source:
            kept.append(row)
            continue

        removed.append(row)
        found = _find_dest_image(body_images_dir, row["body_type"], row["subject_id"])

        if found is None:
            missing_files.append(row["subject_id"])
            continue

        if not dry_run:
            found.unlink()
        deleted_files.append(row["subject_id"])

    if not dry_run:
        _write_labels(labels_path, kept)

    print(f"Removed rows: {len(removed)}")
    counts = {}
    for row in removed:
        counts[row["body_type"]] = counts.get(row["body_type"], 0) + 1
    print(f"  Per-class: {counts}")
    print(f"Files deleted: {len(deleted_files)}")
    if missing_files:
        print(f"Rows removed but file already missing on disk: {len(missing_files)}")
        print(f"  {missing_files}")
    print(f"\nRemaining rows: {len(kept)}")

    if dry_run:
        print("\nDRY RUN - no files deleted, labels.csv not modified.")
    elif removed:
        print(f"\nlabels.csv updated: {labels_path}")
        print(
            "\nNEXT STEP: datasets/body_images_processed/ may still contain stale "
            "processed copies of the removed images - rebuild it:\n"
            "  rm -rf ../../datasets/body_images_processed\n"
            "  python build_dataset.py --source ../../datasets/body_images "
            "--out ../../datasets/body_images_processed"
        )

    return {
        "removed": removed,
        "kept": kept,
        "deleted_files": deleted_files,
        "missing_files": missing_files,
    }


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--dataset-source", type=str, required=True)
    parser.add_argument(
        "--body-images-dir", type=Path, default=Path("../../datasets/body_images")
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would happen without deleting anything",
    )
    args = parser.parse_args()

    remove_dataset_source(
        args.body_images_dir, args.dataset_source, dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
