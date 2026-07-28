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
    python train.py --data ../../datasets/body_images_processed --epochs 50
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.utils import set_random_seed

from data_generator import load_dataset, train_val_split
from model_architecture import CLASS_NAMES, build_model, compile_model

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def train(
    data_dir: Path,
    output_dir: Path,
    epochs: int,
    batch_size: int,
    seed: int,
    monitor: str = "val_loss",
    patience: int = 10,
    model_seed: int = None,
):
    """`seed` controls only the train/val split (data_generator.py), so
    every run compares against the exact same validation set. `model_seed`
    (Python/NumPy/TF random state - weight init, dropout masks, batch
    shuffle order) defaults to `seed` but is a separate parameter on
    purpose: to measure genuine run-to-run variance for a fixed
    configuration, vary `model_seed` across runs while holding `seed`
    (and everything else) constant - otherwise each "repeat" would also
    be evaluated against a different validation set, confounding two
    different sources of variation into one number."""
    if model_seed is None:
        model_seed = seed
    set_random_seed(model_seed)

    images, labels = load_dataset(data_dir)
    x_train, x_val, y_train, y_val = train_val_split(images, labels, seed=seed)

    class_weights = compute_class_weight(
        class_weight="balanced", classes=np.arange(len(CLASS_NAMES)), y=y_train
    )
    class_weight_dict = dict(enumerate(class_weights))

    # restore_best_weights=True matters as much as the callback itself -
    # without it, stopping early just keeps whatever the LAST epoch (10
    # epochs past the best one, by construction of `patience`) produced,
    # not the best epoch. mode="auto" infers min-is-better for *_loss and
    # max-is-better for *_accuracy from the monitor name.
    early_stopping = EarlyStopping(
        monitor=monitor,
        patience=patience,
        restore_best_weights=True,
        mode="auto",
        verbose=1,
    )

    model = compile_model(build_model())
    history = model.fit(
        x_train,
        y_train,
        validation_data=(x_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        class_weight=class_weight_dict,
        callbacks=[early_stopping],
        verbose=2,
    )

    actual_epochs = len(history.history["loss"])
    stopped_early = actual_epochs < epochs

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
        "epochs": actual_epochs,
        "max_epochs_requested": epochs,
        "early_stopped": stopped_early,
        "early_stopping_monitor": monitor,
        "early_stopping_patience": patience,
        "seed": seed,
        "model_seed": model_seed,
        "final_train_accuracy": round(float(history.history["accuracy"][-1]), 4),
        "final_val_loss": round(float(val_loss), 4),
    }
    metadata_path = output_dir / f"{version}.json"
    metadata_path.write_text(json.dumps(metadata, indent=2))

    print(f"\nModel saved to {model_path}")
    print(f"Metadata saved to {metadata_path}")
    if stopped_early:
        print(
            f"Stopped early at epoch {actual_epochs}/{epochs} "
            f"({monitor} didn't improve for {patience} epochs; best-epoch weights restored)"
        )
    else:
        print(
            f"Ran the full {actual_epochs} requested epochs without triggering early stopping"
        )
    print(
        f"Validation accuracy: {val_accuracy:.4f}  |  Validation loss: {val_loss:.4f}"
    )
    print(
        f"\nNOTE: trained on {len(x_train) + len(x_val)} images ({len(x_train)} train / "
        f"{len(x_val)} val) from datasets/body_images_processed/. See "
        "documentation/module_reports/module9.md and datasets/datasets_README.md for "
        "which sources/rows in the current dataset (if any) have known label-quality "
        "issues. This run alone proves the training pipeline runs end to end, not "
        "that the resulting model is fit for real classification - check the "
        "per-epoch train/val accuracy gap for overfitting before trusting the final "
        "number."
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
    parser.add_argument(
        "--epochs",
        type=int,
        default=15,
        help="Maximum epochs - early stopping may end the run sooner",
    )
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument(
        "--seed", type=int, default=42, help="Controls only the train/val split"
    )
    parser.add_argument(
        "--model-seed",
        type=int,
        default=None,
        help="Controls weight init/dropout/batch order (default: same as --seed). "
        "Vary this across repeated runs to measure genuine run-to-run variance "
        "without also changing which images land in validation.",
    )
    parser.add_argument(
        "--monitor",
        type=str,
        default="val_loss",
        help="Metric EarlyStopping watches (e.g. val_loss, val_accuracy)",
    )
    parser.add_argument(
        "--patience",
        type=int,
        default=10,
        help="Epochs to wait for --monitor to improve before stopping",
    )
    args = parser.parse_args()

    train(
        args.data,
        args.out,
        args.epochs,
        args.batch_size,
        args.seed,
        monitor=args.monitor,
        patience=args.patience,
        model_seed=args.model_seed,
    )


if __name__ == "__main__":
    main()
