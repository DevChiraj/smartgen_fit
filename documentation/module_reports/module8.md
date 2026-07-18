# Module 8 — AI Dataset Preparation

**Status:** Complete
**Branch:** `feature/module-8-dataset-preparation` → `dev`

## The research trail (why this took longer than "download a dataset")

Per `CLAUDE.md` rule 6, the mandate was Kaggle-first, manual/synthetic fallback only if coverage is genuinely incomplete. Here's what was actually tried, in order:

1. **Kaggle, via the real API** (not just web search) — 12+ targeted queries (`body type`, `somatotype`, `body silhouette`, `obesity image`, `physique classification`, etc.). Every image-bearing candidate was either purely tabular (no photos at all — e.g. `tapakah68/body-measurements-dataset` is just a PDF + CSV) or had photos with **no body-type/BMI label attached** (e.g. `unidpro/body-measurements-image-dataset` — raw per-subject measurement close-ups, no classification metadata). Nothing usable.
2. **Hugging Face** — same story. One candidate (`batuhanince/smolVLM_bodytype`) had a slim/muscular/oversize taxonomy that doesn't map to our Thin/Normal/Overweight scheme, was gated, and its own filenames (`_aug_`, `_denoised`) suggested it was already synthetically augmented — not a real source itself.
3. **A user-supplied Hugging Face link** (`ud-biometrics/body-measurements-image-dataset`) turned out to be the same vendor's (UniData) free teaser sample — 6 people, no body-type labels, marketing material for a paid product.
4. **A locally-prepared dataset was found already sitting in the repo** (`prepare_real_data.py`, `augment_thin.py`, `labels.csv`, `datasets/body_images/`) from outside this session. Inspecting it directly (not trusting the description) found every one of its 43 label rows pointed to the exact same source file — a 400×400 company logo, not a body photo, with fabricated height/weight/BMI numbers attached. **This was discarded, not used.** Flagged directly rather than silently proceeding, since training on it would have been academically indefensible.
5. **A second, genuine attempt** was found: `UniqueData/body-measurements-dataset` on Hugging Face, downloaded via `huggingface_hub` (confirmed via its local cache metadata — a real download, not fabricated) into `raw_dataset/`. This is the same UniData vendor's *fuller* free sample: 21 real, consenting subjects with real height/weight/age/gender/race per `measurements.json`, license **CC-BY-NC-ND-4.0**. One of the photos was inspected directly to confirm — it's a real, identifiable person in a real home setting, not a stock photo or scrape.

That's the dataset this module ended up using: **real, but small (21 subjects) and license-restricted (non-commercial, no redistribution).**

## What was built

### Real-data pipeline (`ai_model/preprocessing/`)
- **`label_dataset_by_bmi.py`** — general-purpose: takes any photos+measurements source, computes BMI from real height/weight, buckets into thin/normal/overweight using the project's own `bmi_categories` thresholds (label is ground-truth-derived, not eyeballed). Two real bugs were found and fixed while verifying it against the actual data:
  - **Silent data loss**: the fallback subject-ID (used when a manifest has no explicit ID field) was `origin.stem` — the JSON filename. This vendor names every subject's sidecar file identically (`measurements.json`), so all 21 subjects collapsed to the same ID, and later writes silently overwrote earlier ones. Result: only 3 of 21 images survived a first run. Fixed to prefer the parent folder name (the actual per-subject identifier for this layout), plus added a same-run collision guard that disambiguates instead of ever overwriting silently again.
  - **Ambiguous image selection**: when a subject has multiple candidate photos (front/side/selfie) and no explicit "which one" field, the fallback picked whichever file iteration happened to return first — not guaranteed to be the front-facing shot the classifier needs. Fixed to explicitly prefer filenames containing "front".
- Running the fixed script against `raw_dataset/` reproduces all **21 real, uniquely-labeled images** (confirmed via distinct MD5 checksums): 11 normal, 10 overweight, 0 thin (this source sample simply has no subject with BMI < 18.5).

### Synthetic supplement (clearly flagged, never conflated with real data)
- **`generate_synthetic_dataset.py`** — procedurally draws simple humanoid silhouettes (PIL primitives, not a GAN, not scraped) with per-class torso-width ranges and internally-consistent fake height/weight/BMI. Used **only** to fill the empty `thin` class (15 images generated). Every row it writes has `source=synthetic`.
- **`augment_dataset.py`** (fixed from the pre-existing `augment_thin.py`: the original used `rotate()` without `expand=True`, silently cropping image corners) — derives flip/rotate variants from images that already exist in a class folder. Tags output `source=augmented`. Not run against the real classes this session (11/10 was judged close enough for a placeholder-stage dataset), but verified working.
- `labels.csv` now has a `source` column (`real` / `synthetic` / `augmented`) on every row — provenance is always traceable, never inferred.

### OpenCV preprocessing pipeline (`opencv_pipeline.py`, `dataset_validator.py`, `build_dataset.py`)
This is the actual Module 8 deliverable per `SYSTEM.md` §6 — implements the "Preprocessing" + "OpenCV Processing" + "Body Detection" stages (feature extraction/classification is Module 9's job, untouched here):
- `dataset_validator.py`: rejects unsupported extensions, corrupt/undecodable files, and images below a minimum size, before anything touches the CNN pipeline.
- `opencv_pipeline.py`: HOG person detection → crop to body with padding (falls back to the full frame when no person is detected, which happens on tightly-cropped close-up photos) → bilateral denoise → CLAHE contrast/lighting normalization (on the L channel only, so color isn't distorted) → resize to a fixed size.
- `build_dataset.py`: orchestrates validate → preprocess → write to `datasets/body_images_processed/<class>/`, printing per-class counts and the body-detection hit rate.

## How to test locally

```
cd ai_model
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt
pip install pytest black flake8
pytest tests/                                              # 23 passed
black preprocessing/ tests/ && flake8 --max-line-length=100 --extend-ignore=E203,W503 preprocessing/ tests/

# Regenerate the dataset (raw_dataset/ and datasets/body_images/ are gitignored, not committed):
python preprocessing/label_dataset_by_bmi.py --source ../raw_dataset --out ../datasets/body_images
python preprocessing/generate_synthetic_dataset.py --out ../datasets/body_images --classes thin --count 15
python preprocessing/dataset_validator.py --dataset ../datasets/body_images
python preprocessing/build_dataset.py --source ../datasets/body_images --out ../datasets/body_images_processed
```

## Verification performed this session

- 23/23 pytest passing across the four preprocessing modules (BMI classification boundaries, unit conversions, front-image selection, OpenCV pipeline shape correctness on synthetic test images, validator accept/reject cases, synthetic generator output correctness). `black`/`flake8` clean (manually run — `ai_model/` isn't wired into CI yet, flagged below).
- Ran the **full real pipeline end-to-end**, not just unit tests: regenerated the real 21-image dataset from `raw_dataset/` (confirmed via MD5 checksums that all 21 are unique files, not duplicates — this is exactly the check that caught the fabricated-logo dataset earlier), generated 15 synthetic `thin` images, validated all 36, and ran `build_dataset.py` against the full set — 36/36 processed, 0 skipped, 19/36 (53%) got a real HOG body-crop and the rest correctly fell back to the full frame rather than erroring.
- **Visually inspected actual output images** (not just checked exit codes): one real "overweight" photo before/after preprocessing, and one synthetic "thin" silhouette before/after — both show correct resize, sane contrast normalization, and no corruption.

## Deferred / known limitations (flagging honestly, not hiding)

- **21 real images is not enough to train a generalizing CNN.** This dataset is sized for building and proving the pipeline, not for producing a model with real predictive validity. Module 9 needs either substantially more real data or an explicit framing as a proof-of-concept, not a deployable classifier.
- **`resize_image()` squashes to a square without preserving aspect ratio** — for a classifier whose entire signal is body proportions, this is worth revisiting (letterbox-pad instead of stretch) before Module 9 finalizes training.
- **HOG body detection only succeeds ~53% of the time** on this dataset's close-range, indoor photos; the rest use the full uncropped frame. Acceptable for now — flagged in case crop accuracy turns out to matter for training quality.
- **License**: the 21 real images are CC-BY-NC-ND-4.0 (non-commercial, no redistribution). Fine for this non-commercial student project, but they must never be committed to git or redistributed — enforced via `.gitignore` (`raw_dataset/`, `datasets/body_images/*`, `datasets/body_images_processed/`), not just convention.
- **`ai_model/` has its own venv and isn't wired into CI** — `backend-ci.yml`/`frontend-ci.yml` don't cover it. Worth adding an `ai-ci.yml` in a later module once the training pipeline (Module 9) exists too, rather than standing up CI for preprocessing alone.
- A Kaggle API credential was shared in this session to support the research; it's stored locally at `~/.kaggle/kaggle.json` (outside the repo, gitignored by default, never committed) but was typed into chat, so per earlier advice it should be rotated.

## Next

Module 9 — CNN training pipeline (`ai_model/training/`), export a versioned model to `ai_model/saved_models/`, record it in the `ai_model_files` table.
