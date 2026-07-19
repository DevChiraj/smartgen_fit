# Datasets

- `body_images/` — class-labeled subfolders (`thin/`, `normal/`, `overweight/`) for CNN training. **Not committed to git** (see below) — regenerate locally with the steps in this file.
- `body_images_processed/` — output of the OpenCV preprocessing pipeline (resized/denoised/contrast-normalized), also not committed. Regenerate with `build_dataset.py` (step 4 below).
- `sri_lankan_foods/` — CSV nutrition data (food name, category, calories, macros, vitamins, minerals) that seeds the `sri_lankan_foods` table.

Large raw datasets and derived image sets are gitignored — keep only code (labeling/preprocessing scripts, this README) in version control, never the images themselves.

## Sourcing `body_images/` (Module 8)

No public dataset ships pre-labeled with Thin/Normal/Overweight folders — verified against both Kaggle (12+ search queries via the real API) and Hugging Face (multiple searches). What's available instead is real body photos paired with real height/weight measurements from a handful of vendors. The fix used here: derive the label from BMI using the project's own `bmi_categories` thresholds, rather than eyeballing photos.

### 1. Download a measurements+photos source dataset

The free sample from **UniqueData** (a commercial anthropometric data vendor) is what this project currently uses — real, consenting participants, 21 usable subjects, license **CC-BY-NC-ND-4.0** (non-commercial, no redistribution of the raw images — fine for this non-commercial student project, but don't commit or republish the photos themselves, hence the gitignore).

```bash
pip install huggingface_hub
python -c "
from huggingface_hub import snapshot_download
snapshot_download(repo_id='UniqueData/body-measurements-dataset', repo_type='dataset', local_dir='raw_dataset')
"
```

Alternatives if you want more coverage (untested by this project, same vendor family, same license terms likely apply — check before use):
- `kaggle datasets download -d unidpro/body-measurements-image-dataset` (needs a Kaggle API token in `~/.kaggle/kaggle.json`)
- `kaggle datasets download -d tapakah68/body-measurements-dataset`

### 2. Label by BMI

```bash
python ai_model/preprocessing/label_dataset_by_bmi.py \
  --source raw_dataset/ \
  --out datasets/body_images \
  --height-unit cm --weight-unit kg
```

If it finds 0 usable records against a different source dataset, re-run with `--dump-fields` to see what field names the manifest actually uses, then adjust `HEIGHT_ALIASES` / `WEIGHT_ALIASES` / `IMAGE_ALIASES` at the top of the script.

### 3. Fill/balance thin classes with clearly-flagged synthetic images

The UniqueData sample happens to have zero subjects with BMI < 18.5 — real "thin" coverage is empty. Rather than block or fabricate fake real-looking data, generate honestly-labeled synthetic silhouettes:

```bash
python ai_model/preprocessing/generate_synthetic_dataset.py \
  --out datasets/body_images --classes thin --count 15
```

Every row this writes to `labels.csv` has `source=synthetic`; every row from step 2 has `source=real`. Never edit that column by hand — it's the whole point of the traceability. To pad an under-represented real class instead of adding a synthetic one (e.g. more `overweight` variants), use `augment_dataset.py`, which only derives flip/rotate variants from images that already exist and tags them `source=augmented`:

```bash
python ai_model/preprocessing/augment_dataset.py \
  --class-dir datasets/body_images/overweight --target-count 15
```

### 4. Validate and preprocess

```bash
python ai_model/preprocessing/dataset_validator.py --dataset datasets/body_images
python ai_model/preprocessing/build_dataset.py \
  --source datasets/body_images --out datasets/body_images_processed --size 224
```

`build_dataset.py` runs the full OpenCV pipeline (`opencv_pipeline.py`) per image: HOG person detection + crop (falls back to the full frame when no person is detected, which is common on tightly-cropped close-up photos), denoise, CLAHE contrast normalization, resize. It prints a per-class count and the body-detection hit rate — check both before training.

## Update (Module 9): dataset expanded to 3 sources, 48 images

Since Module 8, the dataset was expanded with two more sources merged into the same `labels.csv` (`ai_model/preprocessing/prepare_real_dataset_multi_source.py`, added by the project owner):

- `hf_*` (21 images) — the original Hugging Face `UniqueData/body-measurements-dataset` sample from Module 8.
- `kaggle_*` (6 images) — pulled from `raw_dataset/kaggle_data/`. Its `Body Measurements Image Dataset.csv` matches the *other* free teaser sample from the same vendor family seen during Module 8's research (`ud-biometrics` on Hugging Face), not an independent Kaggle-sourced dataset. 3 of the 6 are byte-identical to 3 already-counted `hf_*` photos (same people).
- `ds3_*` (21 images) — a separate university-style "body shape data collection study" (see `raw_dataset/dataset3/Proceedure.pdf`). **Important:** that study's own documented procedure only records height + frontal bust/waist/hip circumference + a photo — it does not include weight. The `weight_kg` column in `measurements_2.csv` was added by someone after the fact and is not a real measurement; visually checking several `ds3_*` photos against their claimed BMI confirms the numbers don't match what's shown (e.g. a normal-looking subject labeled BMI 7.7, which would be visibly skeletal).

**Explicit project decision (documented here so it isn't mistaken for an oversight):** the project owner's supervisor instructed keeping all 48 images exactly as-is — including the `dataset_3` mismatch and the `hf`/`kaggle` duplicates — because the immediate goal is proving the training pipeline runs end to end, not achieving real classification accuracy. See `documentation/module_reports/module9.md` for the full review trail and the resulting model's real (expectedly poor/overfit) metrics. **Do not point Module 10's inference at this model expecting meaningful predictions** — retrain on a corrected/larger dataset first if real accuracy is ever needed.

## Known limitations

- Per the above, roughly half of `labels.csv`'s rows (the `ds3_*` ones) do not have trustworthy body-type labels, and 3 rows are exact duplicates of other rows.
- `resize_image()` squashes to a square without preserving aspect ratio, which distorts body proportions — the exact signal this classifier depends on. Worth revisiting (e.g. letterbox-pad instead of stretch) if this pipeline is ever pointed at real training.
- HOG person detection succeeds on roughly 35/48 images (73%) of this combined dataset's close-range, indoor, tightly-cropped photos; the rest fall back to using the full frame uncropped.
- 48 images total (even before discounting the issues above) is nowhere near enough to train a CNN that generalizes to real-world photos.
