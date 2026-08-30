"""Validates raw dataset images before they're fed to the preprocessing
pipeline: type, dimensions, and whether the file actually decodes as an
image (catches truncated downloads / renamed non-images)."""

from pathlib import Path

from PIL import Image, UnidentifiedImageError

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MIN_DIMENSION = 100


def validate_image(path: Path):
    """Returns None if valid, or a short string reason if not."""
    path = Path(path)
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return f"unsupported extension: {path.suffix}"

    try:
        with Image.open(path) as img:
            img.verify()
        with Image.open(path) as img:
            width, height = img.size
    except (UnidentifiedImageError, OSError):
        return "not a valid/decodable image"

    if width < MIN_DIMENSION or height < MIN_DIMENSION:
        return f"too small ({width}x{height}, minimum {MIN_DIMENSION}px per side)"

    return None


def validate_dataset(root: Path):
    """Walks root/<class>/*.{jpg,png,...} and returns (counts, problems)."""
    root = Path(root)
    counts = {}
    problems = []

    for class_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        images = [p for p in class_dir.iterdir() if p.is_file()]
        counts[class_dir.name] = 0
        for image_path in images:
            reason = validate_image(image_path)
            if reason:
                problems.append((str(image_path), reason))
            else:
                counts[class_dir.name] += 1

    return counts, problems


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset", type=Path, required=True, help="e.g. datasets/body_images"
    )
    args = parser.parse_args()

    counts, problems = validate_dataset(args.dataset)

    print("Valid image counts per class:")
    for cls, count in counts.items():
        print(f"  {cls}: {count}")

    if problems:
        print(f"\n{len(problems)} problem(s) found:")
        for path, reason in problems:
            print(f"  - {path}: {reason}")
    else:
        print("\nNo problems found.")


if __name__ == "__main__":
    main()
