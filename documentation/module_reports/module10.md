# Module 10 — Image Analysis Module

**Status:** Complete
**Branch:** `feature/module-10-image-analysis` → `dev`

## Scope note

Per `SYSTEM.md`'s module boundaries, this module stops at **classification and storage**
(`image_analysis_records`) — it does not look up or create meal/workout recommendations.
`RecommendationService` and `user_recommendations` are explicitly Module 11's job, keeping the
AI/recommendation boundary intact (rule 1). Dashboard's "latest plan" widget therefore still shows
its Module 7 empty state after this module — that's expected, not a bug, until Module 11 exists.

Per the explicit decision at the end of Module 9, this ships the proof-of-concept model as-is,
with a clear in-product disclaimer rather than hiding or overselling its accuracy.

## What was built

### `ai_model/inference/predict.py`
Loads a trained `.keras` model and classifies one image. Critically, it reuses the **exact same**
OpenCV preprocessing functions from `ai_model/preprocessing/opencv_pipeline.py` that built the
training set (HOG body-crop, denoise, CLAHE contrast normalization, resize) — not a
reimplementation. Train/inference preprocessing mismatch is a classic, easy-to-miss correctness bug
(the model would see a different input distribution than it learned on); calling the same functions
by import, not by copy-paste, makes that mismatch structurally impossible. Caches the loaded model
in memory so repeated requests don't reload it from disk each time.

### Backend (`backend/`)
- **`POST /api/v1/image-analysis`** (protected multipart upload) → validate → save → classify →
  store → return the record. **`GET /api/v1/image-analysis/history`** (protected, newest 20) and
  **`GET /api/v1/image-analysis/uploads/<filename>`** (serves the saved photo, same pattern as
  Module 4's profile pictures).
- **`app/ai_inference.py`**: the only place backend code imports `ai_model/` code — one narrow
  `classify_body_image()` function, deferred-imported so TensorFlow only loads when actually
  classifying (not at every app startup/test run). This is also the seam tests mock instead of
  loading the real model.
- **`image_analysis_service.py`**: looks up the *active* model from `ai_model_files` (raises a
  clear 503 if none is registered — a real, handled state, not a crash), validates/saves the upload,
  classifies, maps the CNN's lowercase label (`"normal"`) to the seeded `BodyTypeCategory` row
  case-insensitively (`"Normal"`), and stores the record.
- **Backend now depends on OpenCV + TensorFlow directly** (`opencv-python-headless`, `tensorflow`
  added to `backend/requirements.txt`), because `SYSTEM.md`'s architecture has the backend service
  load `ai_model/inference/predict.py` in-process, not via a subprocess or separate service. This
  does mean TensorFlow is now installed in *two* venvs (`ai_model/.venv` and `backend/.venv`) —
  flagged as a possible dedup target for Module 17 (deployment/containerization), not fixed here.
- **Reused Module 4's file-validation helper for a second purpose**: `validate_and_save_profile_picture`
  was already fully generic (folder/extensions/size-cap all passed as parameters) — renamed to
  `validate_and_save_image` and reused as-is for body photos rather than duplicating the same
  extension/size/real-image-content checks a second time.

### Frontend (`frontend/`)
- **`pages/ImageAnalysis.jsx`** at `/analyze` (new `AuthenticatedLayout` tab, and Dashboard's
  "Analyze body photo" quick action is now a real link instead of the disabled placeholder from
  Module 7): file picker with an immediate local preview, upload, a result card (body-type badge +
  confidence %), and a history grid of past analyses with thumbnails.
- **An explicit, visible demo disclaimer** at the top of the page ("Demo classifier. This model was
  trained on a small proof-of-concept dataset... Results here are for demonstration only") — directly
  implementing the "ship as an explicit demo" decision in the product itself, not just in internal
  docs.

## How to test locally

**Backend**
```
cd backend
pytest                # 56 passed
flake8 .               # clean
flask run
curl -X POST localhost:5000/api/v1/image-analysis -H "Authorization: Bearer <token>" \
  -F "image=@some_photo.jpg"
```

**Frontend**
```
cd frontend
npm run lint     # 0 errors, 1 pre-existing benign warning
npm run build    # succeeds
npm run dev      # log in, visit /analyze
```

## Verification performed this session

- 56/56 backend pytest passing (7 new: auth required, 503 with no active model, non-image rejected,
  a mocked-inference success case checking the full response shape and that the served image is
  fetchable, history isolation between two users, and the no-matching-body-type error path).
  32/32 ai_model pytest passing (2 new for `predict.py`: builds a *throwaway* untrained model in the
  test itself so the pipeline is exercised without depending on the real gitignored 38 MB model
  file, and confirms the model-loading cache actually avoids a second disk load). `flake8`/`black`
  clean on both sides.
- **Caught and fixed a real test-isolation bug while verifying**: the new image-analysis tests were
  writing real files into the actual tracked `uploads/body_images/` folder instead of a temp
  directory — the same isolation `conftest.py` already had for profile pictures (Module 4) was
  missing for body images. Fixed by adding `BODY_IMAGE_UPLOAD_FOLDER` to the test fixture override;
  confirmed by re-running the suite and checking the real folder for leaked files (none).
- **Full real-stack verification**: started the backend against real MySQL, confirmed the Module 9
  trained model was still registered and active, then via `curl` uploaded a real photo from the
  training set (`hf_0`, a "normal"-labeled subject) and got back a correct `Normal` prediction;
  confirmed history, served-image, and non-image-rejection all work against the real stack.
  Then drove the actual frontend in a headless browser: registered a user, visited `/analyze`,
  confirmed the demo disclaimer and empty history state, uploaded a real "overweight"-labeled photo
  (`hf_1`) through the real file input, and got back a correct `Overweight` prediction with the
  history grid updating — all with zero console errors. Screenshot reviewed directly. Smoke-test
  users, their DB records, and their uploaded files were all cleaned up afterward.

## Deferred / known limitations

- Restated: the underlying model is a proof-of-concept (Module 9), not validated for real accuracy.
  The frontend disclaimer says so explicitly; don't remove it without retraining on better data first.
- TensorFlow/OpenCV now duplicated across `ai_model/.venv` and `backend/.venv` — acceptable for local
  dev, worth consolidating (or containerizing) before a real deployment.
- No image-analysis-specific CI yet (same gap as Modules 8/9, now extended to the backend's new AI
  dependencies) — `backend-ci.yml` will exercise these tests since they're mocked at the
  `classify_body_image` seam, but nothing currently verifies the real TensorFlow/OpenCV path in CI.
- Uploaded body photos are stored the same way profile pictures are (UUID filename, publicly
  fetchable by anyone with the link, not owner-restricted) — same trade-off already accepted and
  documented in Module 4, just noting it now applies to a more sensitive class of photo.

## Next

Module 11 — Recommendation engine: pure rule-based lookup service triggered after classification,
populates `user_recommendations`. This is what will finally make Dashboard's "latest plan" widget
(built empty in Module 7) show real data, and is the natural continuation of what this module's
`image_analysis_records` now produces.
