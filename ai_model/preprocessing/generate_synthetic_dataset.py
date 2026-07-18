"""Generates clearly-labeled synthetic body-silhouette placeholder images.

Used only to fill classes with no real coverage - the UniqueData sample
dataset (see label_dataset_by_bmi.py) happened to have zero subjects
with BMI < 18.5, leaving "thin" empty. These are simple procedural
silhouettes, not real photos or GAN-generated fakes. Every image is
recorded in labels.csv with source="synthetic" so it can never be
mistaken for real training data. Swap in real, properly-licensed
photos for this class before Module 9 trains anything meant to be
evaluated for real.

USAGE
-----
    python generate_synthetic_dataset.py --out ../../datasets/body_images --classes thin --count 15
"""

import argparse
import csv
import random
from pathlib import Path

from PIL import Image, ImageDraw

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

# Roughly matches each class's real BMI range so the "as if real"
# height/weight pairing is at least internally consistent, not just a
# random label slapped on an arbitrary shape.
BMI_RANGE_BY_CLASS = {
    "thin": (15.5, 18.4),
    "normal": (18.5, 24.9),
    "overweight": (25.0, 34.0),
}

TORSO_WIDTH_FACTOR_BY_CLASS = {
    "thin": (0.14, 0.18),
    "normal": (0.20, 0.26),
    "overweight": (0.30, 0.40),
}


def _draw_silhouette(width, height, torso_width_factor, rng):
    background = (rng.randint(230, 250),) * 3
    img = Image.new("RGB", (width, height), color=background)
    draw = ImageDraw.Draw(img)

    center_x = width // 2
    head_radius = int(width * 0.06)
    head_top = int(height * 0.05)

    torso_width = int(width * torso_width_factor)
    torso_top = head_top + head_radius * 2
    torso_bottom = int(height * 0.62)

    leg_top = torso_bottom
    leg_bottom = int(height * 0.95)
    leg_width = int(torso_width * 0.32)

    skin = (rng.randint(150, 220), rng.randint(120, 180), rng.randint(100, 150))

    draw.ellipse(
        [
            center_x - head_radius,
            head_top,
            center_x + head_radius,
            head_top + head_radius * 2,
        ],
        fill=skin,
    )
    draw.rounded_rectangle(
        [
            center_x - torso_width // 2,
            torso_top,
            center_x + torso_width // 2,
            torso_bottom,
        ],
        radius=int(torso_width * 0.2),
        fill=skin,
    )

    arm_width = int(torso_width * 0.18)
    draw.rounded_rectangle(
        [
            center_x - torso_width // 2 - arm_width,
            torso_top + 5,
            center_x - torso_width // 2,
            torso_bottom - 10,
        ],
        radius=arm_width // 2,
        fill=skin,
    )
    draw.rounded_rectangle(
        [
            center_x + torso_width // 2,
            torso_top + 5,
            center_x + torso_width // 2 + arm_width,
            torso_bottom - 10,
        ],
        radius=arm_width // 2,
        fill=skin,
    )

    gap = int(leg_width * 0.4)
    draw.rounded_rectangle(
        [center_x - gap - leg_width, leg_top, center_x - gap, leg_bottom],
        radius=leg_width // 3,
        fill=skin,
    )
    draw.rounded_rectangle(
        [center_x + gap, leg_top, center_x + gap + leg_width, leg_bottom],
        radius=leg_width // 3,
        fill=skin,
    )
    return img


def generate_class(class_name, count, out_dir, start_index=0, seed=None):
    rng = random.Random(seed)
    class_dir = out_dir / class_name
    class_dir.mkdir(parents=True, exist_ok=True)
    bmi_lo, bmi_hi = BMI_RANGE_BY_CLASS[class_name]
    width_lo, width_hi = TORSO_WIDTH_FACTOR_BY_CLASS[class_name]

    rows = []
    for i in range(count):
        idx = start_index + i
        width, height = 400, 800
        torso_factor = rng.uniform(width_lo, width_hi)
        img = _draw_silhouette(width, height, torso_factor, rng)
        img = img.rotate(rng.uniform(-4, 4), expand=False, fillcolor=(240, 240, 240))

        height_cm = round(rng.uniform(155, 185), 1)
        bmi = round(rng.uniform(bmi_lo, bmi_hi), 2)
        weight_kg = round(bmi * (height_cm / 100) ** 2, 1)

        filename = f"{class_name}_synthetic_{idx}.png"
        dest_path = class_dir / filename
        img.save(dest_path)

        rows.append(
            {
                "subject_id": f"synthetic_{class_name}_{idx}",
                "source_image": "generated",
                "dest_image": str(dest_path),
                "height_cm": height_cm,
                "weight_kg": weight_kg,
                "bmi": bmi,
                "body_type": class_name,
                "source": "synthetic",
            }
        )
    return rows


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--out", type=Path, required=True, help="e.g. datasets/body_images"
    )
    parser.add_argument(
        "--classes", nargs="+", default=["thin"], choices=list(BMI_RANGE_BY_CLASS)
    )
    parser.add_argument(
        "--count", type=int, default=15, help="Images to generate per class"
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    labels_path = args.out / "labels.csv"
    existing_rows = []
    if labels_path.exists():
        with open(labels_path, newline="", encoding="utf-8") as f:
            existing_rows = list(csv.DictReader(f))

    all_new_rows = []
    for cls in args.classes:
        rows = generate_class(cls, args.count, args.out, seed=args.seed)
        all_new_rows.extend(rows)
        print(f"Generated {len(rows)} synthetic '{cls}' images.")

    combined = existing_rows + all_new_rows
    with open(labels_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LABEL_FIELDNAMES)
        writer.writeheader()
        writer.writerows(combined)
    print(f"labels.csv updated: {labels_path} ({len(combined)} total rows)")


if __name__ == "__main__":
    main()
