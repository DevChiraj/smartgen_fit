"""Shared feature encoding for the KNN recommender - used identically by
train_recommender.py and recommend.py so inference sees the same feature
space it was trained on (same principle as opencv_pipeline.py being
reused between CNN training and inference).

Features: Age (raw, scaled later by StandardScaler), Gender (binary),
BMI_Category (ordinal). The CNN only ever predicts thin/normal/overweight
(CLASS_NAMES in model_architecture.py) - "obese" only appears on the
training side of this mapping, from the source dataset's own
BMI_Category column, and is never a query-time value.
"""

GENDER_ENCODING = {"male": 0.0, "female": 1.0}
DEFAULT_GENDER_VALUE = 0.5

BMI_CATEGORY_ORDINAL = {
    "thin": 0,
    "underweight": 0,
    "normal": 1,
    "overweight": 2,
    "obese": 3,
}


def encode_gender(gender: str) -> float:
    return GENDER_ENCODING.get(gender.strip().lower(), DEFAULT_GENDER_VALUE)


def encode_bmi_category(label: str) -> int:
    key = label.strip().lower()
    if key not in BMI_CATEGORY_ORDINAL:
        raise ValueError(f"Unknown BMI/body-type category: {label!r}")
    return BMI_CATEGORY_ORDINAL[key]


def build_feature_vector(age: int, gender: str, bmi_category_label: str) -> list[float]:
    return [
        float(age),
        encode_gender(gender),
        float(encode_bmi_category(bmi_category_label)),
    ]
