# Module 9 — CNN Training Pipeline

**Status:** Complete
**Branch:** `feature/module-9-cnn-training` → `dev`

## Read this first: what this module does and does not prove

Per explicit instruction from the project owner's supervisor (relayed mid-session, after two rounds
of dataset review flagged real problems — see below), this module's goal was narrowed to **prove the
training pipeline runs end to end**, not to produce a model with real predictive accuracy. That
instruction is honored here, and the resulting model's honestly-poor metrics reflect it. **Do not
wire Module 10's inference to this model expecting meaningful classifications** — see
`datasets/datasets_README.md` for what would need fixing first (a corrected/larger dataset).

## The dataset review that preceded this module

Before touching training code, the project owner reported the dataset had grown to 48 images across
three merged sources. Two full review passes were done (findings below); after the second, the
decision was made explicitly to keep everything as-is:

- **First review**: found the local dataset was fabricated — 43 label rows all pointing to one
  company logo file. Discarded, real data sourced instead (documented in `module8.md`).
- **Second review** (this module, before training): the 48-image merged set had duplicate images
  (`hf_19`/`kaggle_6` byte-identical) and a serious problem in the third source, `dataset_3` — its
  own documented collection procedure (`raw_dataset/dataset3/Proceedure.pdf`) records height + bust/
  waist/hip circumference + a photo, **not weight**. The `weight_kg` column in its CSV was added
  later by someone and isn't a real measurement — confirmed by checking photos directly against
  their claimed BMI (a visually normal-looking subject labeled BMI 7.7, which would be visibly
  skeletal; another labeled BMI 39.3 that looks like an average build).
- Also found two rows (`hf_12`, `hf_14`) had been deleted from disk during an earlier partial dedup
  attempt, while their `labels.csv` rows remained — restored both from `raw_dataset/` so `labels.csv`
  is at least internally consistent (every row has a real file behind it), without changing which
  images are included.
- **The explicit decision**, after this was all surfaced: keep all 48 images and known issues as-is.
  Documented in `datasets/datasets_README.md` so a future reader doesn't mistake this for an
  oversight.

## What was built

### `ai_model/training/`
- **`model_architecture.py`**: a small CNN (3 conv+pool blocks, dense head, dropout) — deliberately
  shallow, since a deeper architecture (ResNet/VGG-style) would only overfit faster on this dataset's
  size without any benefit. `CLASS_NAMES = ["normal", "overweight", "thin"]` (alphabetical, matching
  the folder iteration order `data_generator.py` and `build_dataset.py` both use).
- **`data_generator.py`**: loads `datasets/body_images_processed/<class>/*` (Module 8's OpenCV output)
  into arrays, stratified train/val split via scikit-learn.
- **`train.py`**: trains, evaluates, saves a versioned `.keras` file to `ai_model/saved_models/`
  (gitignored — large binary), and writes a JSON metadata sidecar (version, accuracy, trained_date,
  class names, counts) next to it. Applies class weights to partially offset the 24/16/8 class
  imbalance. Never touches the database — training stays fully decoupled from the backend.

### Backend registration (`backend/app/`)
- **`repositories/ai_model_file_repository.py`**, **`services/ai_model_registration_service.py`**,
  **`register_model.py`**: a new `flask register-model <metadata.json>` CLI command reads the
  metadata sidecar `train.py` wrote and inserts a row into `ai_model_files`, deactivating any
  previously-active model first. This is the only place training output touches the database — the
  training script itself has zero DB code, matching the same decoupling pattern as `flask seed`.

## How to test locally

```
cd ai_model
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt
pip install pytest black flake8
pytest tests/                    # 30 passed
black training/ tests/ && flake8 --max-line-length=100 --extend-ignore=E203,W503 training/ tests/

python training/train.py --data ../datasets/body_images_processed --epochs 15

cd ../backend
flask register-model ../ai_model/saved_models/<version>.json
```

## Verification performed this session

- 30/30 ai_model pytest passing (7 new: model architecture I/O shapes, compiled loss, data loader
  correctness with synthetic tiny images, stratified split behavior and determinism). 49/49 backend
  pytest passing (3 new: registration creates an active row, deactivates the previous active model,
  rejects a duplicate version). `black`/`flake8` clean on both sides.
- **Actually ran training end to end** against the real 48-image processed dataset (not a synthetic
  smoke test): 15 epochs, training accuracy climbed to 94.7% (expected heavy overfitting on 38
  training images), validation accuracy 60% on the 10-image validation split. These numbers are
  reported honestly, not cherry-picked — they're exactly what "proves the pipeline runs, doesn't
  prove real accuracy" looks like in practice.
- **Loaded the saved `.keras` file back and ran a real prediction** on a dummy input to confirm it's
  a genuinely usable model file, not just something that "saved" without error — output shape
  `(1, 3)`, softmax probabilities correctly summing to 1.
- **Registered the model into the real MySQL database**, then queried it directly to confirm the row
  is correct: `id=1, version=v20260719_134710, accuracy=0.6000, is_active=True`.

## Deferred / known limitations

- Restated from above: this model is not fit for real classification. Retraining on corrected/larger
  data is a prerequisite before Module 10's inference should treat its output as meaningful.
- No data augmentation (flip/rotate/brightness) in the training loop itself — given the dataset's
  actual problems are labeling/duplication, not just volume, augmentation would have added complexity
  without addressing the real issue. Worth adding once training on trustworthy data.
- `ai_model/` still has no CI (same gap flagged in Module 8) — now covers both preprocessing and
  training. Worth setting up once Module 10 (inference) exists too.
- Only one model version exists so far; the `deactivate_all()` / `is_active` mechanics are only
  tested with synthetic versions in `test_ai_model_registration.py`, not a real second training run.

## Next

Module 10 — Image analysis module: upload → validation → OpenCV preprocessing → CNN inference API →
`image_analysis_records`, wired to frontend upload page. Given this module's model isn't fit for real
use, Module 10 should either retrain first or clearly surface to users that classification is a
demo/proof-of-concept, not a validated result.
