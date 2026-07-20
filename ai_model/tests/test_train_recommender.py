import json

import joblib
import pandas as pd

from train_recommender import train


def _make_meal_xlsx(tmp_path):
    df = pd.DataFrame(
        [
            {"Person_ID": "P001", "Age": 20, "Gender": "Male", "BMI_Category": "Thin"},
            {
                "Person_ID": "P002",
                "Age": 70,
                "Gender": "Female",
                "BMI_Category": "Overweight",
            },
            {
                "Person_ID": "P003",
                "Age": 45,
                "Gender": "Male",
                "BMI_Category": "Normal",
            },
        ]
    )
    path = tmp_path / "meal.xlsx"
    df.to_excel(path, index=False)
    return path


def test_train_writes_bundle_metadata_and_active_pointer(tmp_path):
    meal_xlsx = _make_meal_xlsx(tmp_path)
    output_dir = tmp_path / "saved_models"

    metadata = train(meal_xlsx, output_dir)

    bundle_path = output_dir / f"recommender_{metadata['version']}.joblib"
    metadata_path = output_dir / f"recommender_{metadata['version']}.json"
    active_pointer_path = output_dir / "recommender_active.json"

    assert bundle_path.exists()
    assert metadata_path.exists()
    assert active_pointer_path.exists()

    saved_metadata = json.loads(metadata_path.read_text())
    assert saved_metadata["record_count"] == 3

    bundle = joblib.load(bundle_path)
    assert bundle["person_ids"] == ["P001", "P002", "P003"]
    assert "scaler" in bundle and "knn" in bundle
