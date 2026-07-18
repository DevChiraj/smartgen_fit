"""Flip/rotate augmentation to pad out an under-represented class.

Only ever derives new images from existing ones already in
datasets/body_images/<class>/ - it never invents new subjects. Each
augmented file is recorded in labels.csv with source="augmented" and
keeps the originating subject's height/weight/BMI, so provenance stays
traceable back to whichever real or synthetic image it came from.

USAGE
-----
    python augment_dataset.py --class-dir ../../datasets/body_images/overweight --target-count 15
"""

import argparse
import csv
from pathlib import Path

from PIL import Image

AUGMENTATION_PREFIX = "aug"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
LABEL_FIELDNAMES = [
    "subject_id",
    "source_image",
    "dest_image",
    "height_cm",
    "weight_kg",
    "bmi",
    "body_type",
    "source",
]


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


def augment_class(class_dir: Path, labels_path: Path, target_count: int):
    originals = [
        p
        for p in class_dir.iterdir()
        if p.suffix.lower() in IMAGE_EXTENSIONS
        and not p.stem.startswith(AUGMENTATION_PREFIX)
    ]
    if not originals:
        print(f"No source images in {class_dir} to augment from.")
        return

    rows = _read_labels(labels_path)
    by_dest = {row["dest_image"]: row for row in rows}

    existing_count = len(
        [p for p in class_dir.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS]
    )
    created = 0
    i = 0
    while existing_count + created < target_count:
        original = originals[i % len(originals)]
        variant = i % 2
        img = Image.open(original).convert("RGB")

        if variant == 0:
            new_img = img.transpose(Image.FLIP_LEFT_RIGHT)
            tag = "flip"
        else:
            new_img = img.rotate(8, expand=True, fillcolor=(255, 255, 255))
            tag = "rot"

        dest_name = f"{AUGMENTATION_PREFIX}_{tag}_{i}_{original.name}"
        dest_path = class_dir / dest_name
        new_img.save(dest_path)

        source_row = by_dest.get(str(original))
        rows.append(
            {
                "subject_id": source_row["subject_id"] if source_row else original.stem,
                "source_image": str(original),
                "dest_image": str(dest_path),
                "height_cm": source_row.get("height_cm", "") if source_row else "",
                "weight_kg": source_row.get("weight_kg", "") if source_row else "",
                "bmi": source_row.get("bmi", "") if source_row else "",
                "body_type": class_dir.name,
                "source": "augmented",
            }
        )
        created += 1
        i += 1

    _write_labels(labels_path, rows)
    print(
        f"Created {created} augmented images in {class_dir} (now {existing_count + created} total)."
    )


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--class-dir",
        required=True,
        type=Path,
        help="e.g. datasets/body_images/overweight",
    )
    parser.add_argument(
        "--labels",
        type=Path,
        default=None,
        help="labels.csv path (default: sibling of --class-dir)",
    )
    parser.add_argument(
        "--target-count",
        type=int,
        required=True,
        help="Desired total image count for this class",
    )
    args = parser.parse_args()

    labels_path = args.labels or (args.class_dir.parent / "labels.csv")
    augment_class(args.class_dir, labels_path, args.target_count)


if __name__ == "__main__":
    main()
