"""Trains the Module 11 KNN recommender directly from the meal dataset
xlsx (Age/Gender/BMI_Category/Person_ID) - the workout dataset isn't
needed for training since it shares the same Person_ID/Age/Gender and
carries no extra feature signal; recommendation_service fetches the
matched workout row from the DB by Person_ID after inference.

Trained offline only - never invoked from a live request. Writes a
versioned joblib bundle (StandardScaler + fitted NearestNeighbors +
the person_id array in training-row order) to ai_model/saved_models/,
plus a JSON metadata sidecar and a recommender_active.json pointer that
recommend.py reads by default. Kept out of the ai_model_files DB table -
that registry's schema (accuracy, is_active flag tied to CNN retraining
via `flask register-model`) is CNN-specific; a filesystem pointer avoids
overloading it for an unrelated model type.

USAGE
-----
    python train_recommender.py \
      --meal-xlsx ../../datasets/recommendations/Sri_Lankan_Meal_Dataset_Part_1.xlsx
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from encoding import BMI_CATEGORY_ORDINAL, GENDER_ENCODING, build_feature_vector

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def train(meal_xlsx: Path, output_dir: Path):
    df = pd.read_excel(meal_xlsx)

    person_ids = df["Person_ID"].astype(str).tolist()
    features = [
        build_feature_vector(row.Age, row.Gender, row.BMI_Category)
        for row in df.itertuples(index=False)
    ]

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    knn = NearestNeighbors(n_neighbors=1, metric="euclidean")
    knn.fit(scaled_features)

    version = datetime.now(timezone.utc).strftime("v%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)

    bundle = {
        "scaler": scaler,
        "knn": knn,
        "person_ids": person_ids,
        "gender_encoding": GENDER_ENCODING,
        "bmi_category_ordinal": BMI_CATEGORY_ORDINAL,
    }
    bundle_path = output_dir / f"recommender_{version}.joblib"
    joblib.dump(bundle, bundle_path)

    try:
        repo_relative_path = str(bundle_path.resolve().relative_to(REPO_ROOT)).replace(
            "\\", "/"
        )
    except ValueError:
        repo_relative_path = str(bundle_path)

    metadata = {
        "version": version,
        "file_path": repo_relative_path,
        "trained_date": datetime.now(timezone.utc).isoformat(),
        "record_count": len(person_ids),
        "features": ["age", "gender", "bmi_category_ordinal"],
        "source_dataset": str(meal_xlsx),
    }
    metadata_path = output_dir / f"recommender_{version}.json"
    metadata_path.write_text(json.dumps(metadata, indent=2))

    active_pointer_path = output_dir / "recommender_active.json"
    active_pointer_path.write_text(
        json.dumps({"file_path": repo_relative_path}, indent=2)
    )

    print(f"\nRecommender bundle saved to {bundle_path}")
    print(f"Metadata saved to {metadata_path}")
    print(f"Active pointer updated: {active_pointer_path} -> {repo_relative_path}")
    print(f"Trained on {len(person_ids)} records.")

    return metadata


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--meal-xlsx",
        type=Path,
        default=Path(
            "../../datasets/recommendations/Sri_Lankan_Meal_Dataset_Part_1.xlsx"
        ),
    )
    parser.add_argument("--out", type=Path, default=Path("../saved_models"))
    args = parser.parse_args()

    train(args.meal_xlsx, args.out)


if __name__ == "__main__":
    main()
