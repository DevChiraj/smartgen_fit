"""CNN training entry point. Trained offline only - never invoked from
a live request. The backend only ever loads the exported model file
(Module 10); this script never touches the database. It writes a
versioned model to ai_model/saved_models/ plus a JSON metadata sidecar
(version, accuracy, trained_date, ...) that the backend's
`flask register-model <metadata.json>` command (Module 9,
backend/app/register_model.py) reads to populate the ai_model_files
table - keeping ai_model/ and backend/ fully decoupled.

USAGE
-----
    python train.py --data ../../datasets/body_images_processed --epochs 15
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.utils.class_weight import compute_class_weight

from data_generator import load_dataset, train_val_split
from model_architecture import CLASS_NAMES, build_model, compile_model

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def train(data_dir: Path, output_dir: Path, epochs: int, batch_size: int, seed: int):
    images, labels = load_dataset(data_dir)
    x_train, x_val, y_train, y_val = train_val_split(images, labels, seed=seed)

    class_weights = compute_class_weight(
        class_weight="balanced", classes=np.arange(len(CLASS_NAMES)), y=y_train
    )
    class_weight_dict = dict(enumerate(class_weights))

    model = compile_model(build_model())
    history = model.fit(
        x_train,
        y_train,
        validation_data=(x_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        class_weight=class_weight_dict,
        verbose=2,
    )

    val_loss, val_accuracy = model.evaluate(x_val, y_val, verbose=0)

    version = datetime.now(timezone.utc).strftime("v%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / f"{version}.keras"
    model.save(model_path)

    try:
        repo_relative_path = str(model_path.resolve().relative_to(REPO_ROOT)).replace(
            "\\", "/"
        )
    except ValueError:
        repo_relative_path = str(model_path)

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
    }
    metadata_path = output_dir / f"{version}.json"
    metadata_path.write_text(json.dumps(metadata, indent=2))

    print(f"\nModel saved to {model_path}")
    print(f"Metadata saved to {metadata_path}")
    print(
        f"Validation accuracy: {val_accuracy:.4f}  |  Validation loss: {val_loss:.4f}"
    )
    print(
        "\nNOTE: trained on a small (48-image) dataset that includes known "
        "data-quality issues kept in per explicit project direction - see "
        "documentation/module_reports/module9.md. This proves the training "
        "pipeline runs end to end, not that the resulting model is fit for "
        "real classification."
    )

    return metadata


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--data", type=Path, default=Path("../../datasets/body_images_processed")
    )
    parser.add_argument("--out", type=Path, default=Path("../saved_models"))
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    train(args.data, args.out, args.epochs, args.batch_size, args.seed)


if __name__ == "__main__":
    main()
