import pandas as pd

from recommend import find_matching_person
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


def _train_bundle(tmp_path):
    metadata = train(_make_meal_xlsx(tmp_path), tmp_path / "saved_models")
    return tmp_path / "saved_models" / f"recommender_{metadata['version']}.joblib"


def test_find_matching_person_returns_nearest_neighbor(tmp_path):
    bundle_path = _train_bundle(tmp_path)

    assert find_matching_person("thin", 22, "male", str(bundle_path)) == "P001"
    assert find_matching_person("overweight", 68, "female", str(bundle_path)) == "P002"
    assert find_matching_person("normal", 44, "male", str(bundle_path)) == "P003"


def test_find_matching_person_caches_loaded_bundle(tmp_path, monkeypatch):
    import recommend as recommend_module

    bundle_path = _train_bundle(tmp_path)
    recommend_module._bundle_cache.clear()

    load_calls = []
    original_load = recommend_module.joblib.load

    def counting_load(path):
        load_calls.append(path)
        return original_load(path)

    monkeypatch.setattr(recommend_module.joblib, "load", counting_load)

    find_matching_person("thin", 22, "male", str(bundle_path))
    find_matching_person("normal", 44, "male", str(bundle_path))

    assert len(load_calls) == 1
