"""Fine-tunes an already-trained/saved CNN with data augmentation, instead
of training a fresh model from scratch (see train.py for that path).

Loads a previously saved .keras/.h5 model, re-compiles it with a low
learning rate so the existing weights are nudged rather than destroyed,
and continues training on the same dataset - but with real-time
ImageDataGenerator augmentation (rotation/zoom/shift/flip) on the
training split only, never the validation split.

Trained offline only - never invoked from a live request, and this
script never touches the database, same decoupling as train.py. It
writes a new versioned model file plus a JSON metadata sidecar (with a
`base_model` field recording what it was fine-tuned from) that the
backend's `flask register-model <metadata.json>` command can pick up
if you decide to make the fine-tuned model active - that's a separate,
deliberate step this script does not take on its own.

READ THIS FIRST: fine-tuning does not fix the underlying dataset problems
documented in documentation/module_reports/module9.md (fabricated weight
column in one source, duplicates, 48 images total, kept as-is per explicit
project direction). Augmentation only multiplies variations of those same
48 images - it cannot manufacture the additional real, correctly-labeled
subjects the dataset actually needs. Treat this script as what it is: the
augmentation + low-LR continued-training mechanics working end to end, not
a fix for the dataset's known accuracy problems.

USAGE
-----
    python finetune.py --model ../saved_models/v20260719_134710.keras --epochs 12
    python finetune.py  # auto-picks the most recently trained model
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.utils.class_weight import compute_class_weight
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from data_generator import load_dataset, train_val_split
from model_architecture import CLASS_NAMES, compile_model

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SAVED_MODELS_DIR = Path(__file__).resolve().parent.parent / "saved_models"


def _find_latest_model(saved_models_dir: Path) -> Path:
    """Picks the most recently trained model via its metadata sidecar's
    `trained_date`, not file mtime - mtime changes on checkout/copy,
    trained_date doesn't."""
    metadata_files = sorted(saved_models_dir.glob("v*.json"))
    if not metadata_files:
        raise FileNotFoundError(
            f"No versioned model metadata (v*.json) found in {saved_models_dir}. "
            "Pass --model explicitly."
        )

    def _trained_date(path: Path) -> str:
        return json.loads(path.read_text()).get("trained_date", "")

    latest_metadata = max(metadata_files, key=_trained_date)
    metadata = json.loads(latest_metadata.read_text())
    model_path = REPO_ROOT / metadata["file_path"]
    if not model_path.exists():
        raise FileNotFoundError(
            f"Metadata {latest_metadata} points to {model_path}, which doesn't exist."
        )
    return model_path


def _build_train_augmenter() -> ImageDataGenerator:
    """Training-only augmentation. No `rescale` here - the loaded model
    already has its own Rescaling(1/255) layer, so these generators must
    keep yielding raw 0-255 pixel values or images get scaled twice."""
    return ImageDataGenerator(
        rotation_range=20,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.15,
        horizontal_flip=True,
        fill_mode="nearest",
    )


def finetune(
    model_path: Path,
    data_dir: Path,
    output_dir: Path,
    out_name: str,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    seed: int,
):
    model = keras.models.load_model(model_path)

    images, labels = load_dataset(data_dir)
    x_train, x_val, y_train, y_val = train_val_split(images, labels, seed=seed)

    class_weights = compute_class_weight(
        class_weight="balanced", classes=np.arange(len(CLASS_NAMES)), y=y_train
    )
    class_weight_dict = dict(enumerate(class_weights))

    # Re-compile with a low learning rate so fine-tuning nudges the
    # existing weights instead of overwriting what the base model learned.
    compile_model(model, learning_rate=learning_rate)

    train_datagen = _build_train_augmenter()
    train_flow = train_datagen.flow(x_train, y_train, batch_size=batch_size, seed=seed)

    history = model.fit(
        train_flow,
        validation_data=(x_val, y_val),
        epochs=epochs,
        class_weight=class_weight_dict,
        verbose=2,
    )

    val_loss, val_accuracy = model.evaluate(x_val, y_val, verbose=0)

    version = datetime.now(timezone.utc).strftime("v%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path_out = output_dir / out_name
    model.save(model_path_out)

    try:
        repo_relative_path = str(
            model_path_out.resolve().relative_to(REPO_ROOT)
        ).replace("\\", "/")
    except ValueError:
        repo_relative_path = str(model_path_out)

    try:
        base_model_repo_path = str(model_path.resolve().relative_to(REPO_ROOT)).replace(
            "\\", "/"
        )
    except ValueError:
        base_model_repo_path = str(model_path)

    metadata = {
        "version": version,
        "file_path": repo_relative_path,
        "accuracy": round(float(val_accuracy), 4),
        "trained_date": datetime.now(timezone.utc).isoformat(),
        "class_names": CLASS_NAMES,
        "train_count": int(len(x_train)),
        "val_count": int(len(x_val)),
        "epochs": epochs,
        "final_train_accuracy": round(float(history.history["accuracy"][-1]), 4),
        "final_val_loss": round(float(val_loss), 4),
        "fine_tuned": True,
        "base_model": base_model_repo_path,
        "learning_rate": learning_rate,
        "augmentation": {
            "rotation_range": 20,
            "width_shift_range": 0.1,
            "height_shift_range": 0.1,
            "zoom_range": 0.15,
            "horizontal_flip": True,
        },
    }
    metadata_path = model_path_out.with_suffix(".json")
    metadata_path.write_text(json.dumps(metadata, indent=2))

    print(f"\nFine-tuned model saved to {model_path_out}")
    print(f"Metadata saved to {metadata_path}")
    print(f"Base model: {model_path}")
    print(
        f"Validation accuracy: {val_accuracy:.4f}  |  Validation loss: {val_loss:.4f}"
    )
    print(
        "\nNOTE: fine-tuned with augmentation on the same 48-image dataset documented "
        "in documentation/module_reports/module9.md, which has known label-quality "
        "issues kept in per explicit project direction. Augmentation multiplies "
        "variations of those same images - it does not fix mislabeled or fabricated "
        "source data. This is not evidence the model is fit for real classification."
    )
    print(
        "\nThis model is not registered as active. To do that:\n"
        f"  cd ../../backend && flask register-model ../ai_model/saved_models/{metadata_path.name}"
    )

    return metadata


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=None,
        help="Path to the existing .keras/.h5 model to fine-tune "
        "(default: the most recently trained model in --saved-models-dir)",
    )
    parser.add_argument(
        "--saved-models-dir",
        type=Path,
        default=DEFAULT_SAVED_MODELS_DIR,
        help="Where to look for the latest model when --model isn't given",
    )
    parser.add_argument(
        "--data", type=Path, default=Path("../../datasets/body_images_processed")
    )
    parser.add_argument("--out", type=Path, default=Path("../saved_models"))
    parser.add_argument(
        "--out-name",
        type=str,
        default="smartgen_model_retrained.h5",
        help="Filename for the fine-tuned model (.h5 or .keras)",
    )
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=1e-4,
        help="Low LR so fine-tuning doesn't destroy the base model's weights",
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    model_path = args.model or _find_latest_model(args.saved_models_dir)

    finetune(
        model_path=model_path,
        data_dir=args.data,
        output_dir=args.out,
        out_name=args.out_name,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
