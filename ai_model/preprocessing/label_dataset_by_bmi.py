"""
label_dataset_by_bmi.py

Turns a body-measurements-plus-photos dataset (e.g. a Kaggle "body
measurements image dataset") into a class-labeled training set for the
SmartGen Fit CNN: datasets/body_images/{thin,normal,overweight}/.

WHY THIS EXISTS
----------------
No public dataset ships with ready-made Thin/Normal/Overweight folders.
What's actually available (Kaggle, Hugging Face) is real photos paired
with real height/weight per subject. This script computes BMI from
those measurements and buckets each photo using the exact thresholds
the project's own `bmi_categories` table uses, so the label is
ground-truth-derived rather than a subjective visual guess.

USAGE
-----
1. Download and extract a source dataset, e.g. via the Kaggle CLI:
       kaggle datasets download -d unidpro/body-measurements-image-dataset
       unzip body-measurements-image-dataset.zip -d raw_dataset/

2. Run this script against it:
       python label_dataset_by_bmi.py --source raw_dataset/ --out ../../datasets/body_images

3. Inspect the printed summary and `datasets/body_images/labels.csv`
   before using the folder for training — check class balance and read
   through skipped_reasons for anything that needs a second look.

The script does NOT assume an exact manifest schema, because that
varies by dataset vendor and can't be verified without downloading it
first. It searches recursively for:
  - a CSV/TSV manifest with height/weight columns (common aliases below), or
  - per-subject JSON sidecar files sitting next to an image file
and pairs each measurement record with the image in the same folder.

If neither pattern matches your specific download, open the file,
check what --dump-fields shows, and adjust HEIGHT_ALIASES /
WEIGHT_ALIASES / IMAGE_ALIASES below rather than hand-sorting images.
"""

import argparse
import csv
import json
import shutil
import statistics
from pathlib import Path

# --- BMI thresholds — must match the `bmi_categories` table in SYSTEM.md ---
THIN_MAX = 18.5  # BMI < 18.5  -> thin
NORMAL_MAX = 25.0  # 18.5 <= BMI < 25 -> normal, BMI >= 25 -> overweight

# --- Plausibility ranges, used only to flag likely bad/misread data ---
HEIGHT_CM_RANGE = (120, 230)
WEIGHT_KG_RANGE = (25, 250)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

HEIGHT_ALIASES = [
    "height_cm",
    "height",
    "Height",
    "HeightCm",
    "height (cm)",
    "stature_cm",
    "stature",
]
WEIGHT_ALIASES = ["weight_kg", "weight", "Weight", "WeightKg", "weight (kg)", "mass_kg"]
IMAGE_ALIASES = ["image", "image_path", "filename", "file", "photo", "image_file"]
ID_ALIASES = ["id", "subject_id", "person_id", "uid"]


def to_cm(value, unit):
    value = float(value)
    if unit == "cm":
        return value
    if unit == "m":
        return value * 100
    if unit == "in":
        return value * 2.54
    raise ValueError(f"Unknown height unit: {unit}")


def to_kg(value, unit):
    value = float(value)
    if unit == "kg":
        return value
    if unit == "lb":
        return value * 0.453592
    raise ValueError(f"Unknown weight unit: {unit}")


def classify_bmi(bmi):
    if bmi < THIN_MAX:
        return "thin"
    if bmi < NORMAL_MAX:
        return "normal"
    return "overweight"


def find_first_alias(record, aliases):
    for key in aliases:
        if key in record and record[key] not in (None, ""):
            return record[key]
    # case-insensitive fallback
    lower_map = {str(k).lower(): v for k, v in record.items()}
    for key in aliases:
        if key.lower() in lower_map and lower_map[key.lower()] not in (None, ""):
            return lower_map[key.lower()]
    return None


def find_companion_image(folder: Path, stem_hint: str = None):
    images = [p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS]
    if not images:
        return None
    if stem_hint:
        for img in images:
            if img.stem == stem_hint:
                return img
    # Prefer a front-facing shot over side/selfie when a vendor's per-subject
    # folder has more than one candidate image and no explicit "image" field
    # names which one to use - front view is what the classifier needs.
    front_facing = [img for img in images if "front" in img.stem.lower()]
    if front_facing:
        return sorted(front_facing)[0]
    return sorted(images)[0]


def records_from_json_sidecars(source: Path):
    """Walk the tree, treat every .json file as one subject's measurements,
    and pair it with an image file in the same directory."""
    records = []
    for json_path in source.rglob("*.json"):
        try:
            data = json.loads(json_path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if isinstance(data, list):
            # some vendors nest a list of measurement dicts in one file
            for entry in data:
                if isinstance(entry, dict):
                    records.append((entry, json_path.parent, json_path))
        elif isinstance(data, dict):
            records.append((data, json_path.parent, json_path))
    return records


def records_from_csv(csv_path: Path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        sample = f.read(4096)
        f.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        reader = csv.DictReader(f, dialect=dialect)
        return [(row, csv_path.parent, csv_path) for row in reader]


def build_manifest(source: Path):
    """Returns a list of (record_dict, folder_for_image_lookup, origin_file)."""
    records = []
    # Prefer an explicit CSV/TSV manifest if one exists near the root.
    for csv_path in list(source.rglob("*.csv")) + list(source.rglob("*.tsv")):
        try:
            rows = records_from_csv(csv_path)
        except csv.Error:
            continue
        if rows and (
            find_first_alias(rows[0][0], HEIGHT_ALIASES)
            or find_first_alias(rows[0][0], WEIGHT_ALIASES)
        ):
            records.extend(rows)

    if not records:
        records = records_from_json_sidecars(source)

    return records


def organize_dataset(
    source: Path, out_dir: Path, height_unit, weight_unit, mode, dry_run, dump_fields
):
    records = build_manifest(source)
    if not records:
        print(
            "No CSV/TSV manifest or JSON sidecars with height/weight fields were found under",
            source,
        )
        print(
            "Run with --dump-fields to inspect the first record this script does see, "
            "then adjust the alias lists."
        )
        return

    if dump_fields:
        sample_record = records[0][0]
        print(
            "First record found — field names available to match against "
            "HEIGHT_ALIASES/WEIGHT_ALIASES/IMAGE_ALIASES:"
        )
        print(json.dumps(sample_record, indent=2, default=str)[:2000])
        return

    for cls in ("thin", "normal", "overweight"):
        (out_dir / cls).mkdir(parents=True, exist_ok=True)

    labeled_rows = []
    skipped = []
    counts = {"thin": 0, "normal": 0, "overweight": 0}
    bmis = []

    for record, folder, origin in records:
        raw_h = find_first_alias(record, HEIGHT_ALIASES)
        raw_w = find_first_alias(record, WEIGHT_ALIASES)
        image_hint = find_first_alias(record, IMAGE_ALIASES)
        # origin.stem is useless as a fallback ID when every subject's sidecar
        # is named identically (e.g. every "measurements.json") - the
        # per-subject folder name is the real identifier in that layout.
        subject_id = (
            find_first_alias(record, ID_ALIASES) or origin.parent.name or origin.stem
        )

        if raw_h is None or raw_w is None:
            skipped.append((str(origin), "missing height or weight field"))
            continue

        try:
            height_cm = to_cm(raw_h, height_unit)
            weight_kg = to_kg(raw_w, weight_unit)
        except (ValueError, TypeError):
            skipped.append(
                (str(origin), f"unparseable height/weight ({raw_h!r}, {raw_w!r})")
            )
            continue

        if not (HEIGHT_CM_RANGE[0] <= height_cm <= HEIGHT_CM_RANGE[1]):
            skipped.append(
                (
                    str(origin),
                    f"height {height_cm:.1f}cm outside plausible range — check --height-unit",
                )
            )
            continue
        if not (WEIGHT_KG_RANGE[0] <= weight_kg <= WEIGHT_KG_RANGE[1]):
            skipped.append(
                (
                    str(origin),
                    f"weight {weight_kg:.1f}kg outside plausible range — check --weight-unit",
                )
            )
            continue

        image_path = None
        if isinstance(image_hint, str):
            candidate = (
                (folder / image_hint)
                if not Path(image_hint).is_absolute()
                else Path(image_hint)
            )
            if candidate.exists():
                image_path = candidate
        if image_path is None:
            image_path = find_companion_image(folder, stem_hint=str(subject_id))
        if image_path is None:
            skipped.append(
                (str(origin), "no matching image file found in the same folder")
            )
            continue

        bmi = weight_kg / ((height_cm / 100) ** 2)
        cls = classify_bmi(bmi)
        counts[cls] += 1
        bmis.append(bmi)

        dest_name = f"{cls}_{subject_id}_{image_path.name}"
        dest_path = out_dir / cls / dest_name
        collision_suffix = 1
        while any(Path(r["dest_image"]) == dest_path for r in labeled_rows):
            # Two subjects resolved to the same dest_name this run (e.g. a
            # non-unique subject_id) - disambiguate instead of overwriting.
            collision_suffix += 1
            dest_name = f"{cls}_{subject_id}-{collision_suffix}_{image_path.name}"
            dest_path = out_dir / cls / dest_name
        if not dry_run:
            if mode == "copy":
                shutil.copy2(image_path, dest_path)
            else:
                if dest_path.exists():
                    dest_path.unlink()
                dest_path.symlink_to(image_path.resolve())

        labeled_rows.append(
            {
                "subject_id": subject_id,
                "source_image": str(image_path),
                "dest_image": str(dest_path),
                "height_cm": round(height_cm, 1),
                "weight_kg": round(weight_kg, 1),
                "bmi": round(bmi, 2),
                "body_type": cls,
                "source": "real",
            }
        )

    if not dry_run:
        with open(out_dir / "labels.csv", "w", newline="", encoding="utf-8") as f:
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
                    "source",
                ],
            )
            writer.writeheader()
            writer.writerows(labeled_rows)

    print(f"Processed {len(records)} records from {source}")
    print(f"  Labeled: {sum(counts.values())}  |  Skipped: {len(skipped)}")
    print(
        f"  Class counts: thin={counts['thin']}  normal={counts['normal']}  "
        f"overweight={counts['overweight']}"
    )
    if bmis:
        print(
            f"  BMI range: {min(bmis):.1f}-{max(bmis):.1f}, "
            f"mean {statistics.mean(bmis):.1f}, median {statistics.median(bmis):.1f}"
        )
    if skipped:
        print(f"\n  {len(skipped)} records skipped, first 10 reasons:")
        for path, reason in skipped[:10]:
            print(f"    - {path}: {reason}")
    if dry_run:
        print("\n  (--dry-run: no files were written)")
    else:
        print(f"\n  Labeled dataset written to: {out_dir}")
        print(f"  Manifest: {out_dir / 'labels.csv'}")

    smallest = min(counts.values()) if counts.values() else 0
    largest = max(counts.values()) if counts.values() else 0
    if smallest and largest and largest / max(smallest, 1) > 3:
        print(
            "\n  WARNING: class counts are heavily imbalanced (largest class is "
            f"{largest / smallest:.1f}x the smallest). Consider augmentation or "
            "collecting more data for the underrepresented class(es) before training."
        )


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--source",
        required=True,
        type=Path,
        help="Root folder of the extracted source dataset",
    )
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="Output folder, e.g. datasets/body_images",
    )
    parser.add_argument("--height-unit", choices=["cm", "m", "in"], default="cm")
    parser.add_argument("--weight-unit", choices=["kg", "lb"], default="kg")
    parser.add_argument(
        "--mode",
        choices=["copy", "symlink"],
        default="copy",
        help="copy is safer; symlink saves disk space",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would happen without writing files",
    )
    parser.add_argument(
        "--dump-fields",
        action="store_true",
        help="Print the first record's fields and exit — use this if 0 records are found",
    )
    args = parser.parse_args()

    if not args.source.exists():
        raise SystemExit(f"--source path does not exist: {args.source}")

    organize_dataset(
        args.source,
        args.out,
        args.height_unit,
        args.weight_unit,
        args.mode,
        args.dry_run,
        args.dump_fields,
    )


if __name__ == "__main__":
    main()
