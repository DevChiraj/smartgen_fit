"""Orchestrates dataset prep for training: validate -> preprocess -> report.

    python build_dataset.py --source ../../datasets/body_images \
        --out ../../datasets/body_images_processed

Only ever reads from --source and writes resized/normalized copies to
--out; the source labels.csv is untouched. Run this after the labeling
and (optional) synthetic/augmentation scripts, right before Module 9
consumes the output.
"""

import argparse
from pathlib import Path

from dataset_validator import validate_image
from opencv_pipeline import preprocess_and_save


def build_dataset(source: Path, out: Path, output_size=(224, 224)):
    class_dirs = sorted(p for p in source.iterdir() if p.is_dir())
    if not class_dirs:
        print(f"No class subfolders found under {source}")
        return

    total_ok = 0
    total_skipped = 0
    total_no_body_detected = 0
    counts = {}

    for class_dir in class_dirs:
        cls = class_dir.name
        counts[cls] = 0
        for image_path in sorted(class_dir.iterdir()):
            if not image_path.is_file():
                continue

            reason = validate_image(image_path)
            if reason:
                print(f"  SKIP {image_path}: {reason}")
                total_skipped += 1
                continue

            dest_path = out / cls / image_path.name
            try:
                body_detected = preprocess_and_save(image_path, dest_path, output_size)
            except ValueError as exc:
                print(f"  SKIP {image_path}: {exc}")
                total_skipped += 1
                continue

            if not body_detected:
                total_no_body_detected += 1
            total_ok += 1
            counts[cls] += 1

    print("\nProcessed dataset written to:", out)
    print("Per-class counts:", counts)
    print(f"Total processed: {total_ok}  |  Skipped (invalid): {total_skipped}")
    print(
        f"Body detected via HOG: {total_ok - total_no_body_detected}/{total_ok} "
        f"(the rest fell back to the full frame - expected for tightly-cropped "
        f"close-up photos, which most of this dataset is)"
    )


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--source", type=Path, required=True, help="e.g. datasets/body_images"
    )
    parser.add_argument(
        "--out", type=Path, required=True, help="e.g. datasets/body_images_processed"
    )
    parser.add_argument(
        "--size", type=int, default=224, help="Output image is size x size"
    )
    args = parser.parse_args()

    build_dataset(args.source, args.out, output_size=(args.size, args.size))


if __name__ == "__main__":
    main()
