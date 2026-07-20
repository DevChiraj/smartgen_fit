# Module 11 — Recommendation Engine (KNN Similarity Match)

**Status:** Complete
**Branch:** `feature/module-11-ml-recommendations` → `dev`

## Architecture decision: this module changes a non-negotiable rule

The original `CLAUDE.md`/`SYSTEM.md` rule 2 was "recommendations are rule-based DB lookups only,
keyed on Body Type + BMI Category + Age Group + Gender." The project owner's request for this
module explicitly asked to move away from that — a real KNN/similarity-based ML recommender,
trained on two newly-supplied datasets (`Sri_Lankan_Meal_Dataset_Part_1.xlsx`,
`Workout_Dataset_Matched_Advanced.xlsx`, 2,000 rows each, joined by `Person_ID`) — which directly
conflicts with the standing rule.

This was flagged back to the project owner before any code was written, with three options: build
the full ML system and formally amend the rule, keep the rule-based design but use the richer
datasets as extra template content, or get clarification on scope. **The project owner chose the
first option** — full ML system, rule amended, supervisor-approved. `CLAUDE.md` rule 2 and
`SYSTEM.md` §1/§2/§4/§6/§11 have been rewritten accordingly (see those files' diffs). Rule 1 (the
CNN only classifies, never generates) is unchanged and still holds: the KNN model doesn't generate
anything either — it always resolves to an existing, real dataset row read verbatim from the DB.

## What was built

### Pre-existing infrastructure bug found and fixed: MySQL tables were silently running on MyISAM

While generating this module's Alembic migration, autogenerate proposed adding FK constraints to
`meal_plans`, `workout_plans`, `image_analysis_records`, and `user_recommendations` that the
SQLAlchemy models had declared since Module 2. Querying the real database directly
(`inspect(engine).get_foreign_keys(...)`) confirmed all four had **zero** enforced FKs. Root cause:
this MySQL 8.3 server has `default_storage_engine = MyISAM` (non-standard — MySQL normally
defaults to InnoDB), so every table since Module 2 silently inherited MyISAM, which MySQL creates
successfully even when a migration's `CREATE TABLE` includes `FOREIGN KEY` clauses — it just
silently ignores them. MyISAM also has no transaction support, so `db.session.rollback()` has never
actually rolled back anything on this database.

Flagged to the project owner via `AskUserQuestion`; chose the full fix. This migration now converts
**every** existing table to InnoDB (`ALTER TABLE ... ENGINE=InnoDB`) before adding any FK
constraints, and explicitly sets `mysql_engine='InnoDB'` on the two new Module 11 tables (otherwise
they'd inherit the same broken MyISAM default). Verified after `flask db upgrade`: all 12 real
tables now report `InnoDB`, and every FK the models declare is now actually enforced in
`information_schema`. Zero rows were lost — the two affected tables with real data (`meal_plans`,
`workout_plans`, 6 rows each) converted cleanly; `user_recommendations`/`image_analysis_records`
were empty at the time.

### Database (`backend/migrations/`, `backend/app/models/`)
- **`meal_recommendation_records`** / **`workout_recommendation_records`** — the KNN candidate pool,
  not a small template table. One row per `Person_ID` from each dataset; `workout_recommendation_records.person_id`
  is a real FK into `meal_recommendation_records.person_id` (verified 1:1, no orphans either
  direction, before the constraint was added).
- **`user_recommendations.matched_person_id`** (new, nullable FK into `meal_recommendation_records`) —
  `meal_plan_id`/`workout_plan_id` kept nullable for backward compatibility with the original
  template design, but no longer populated by the live pipeline.
- Migration: `cc1fb4a9af40_add_ml_recommendation_record_tables_and_.py`, applied against the real
  local MySQL.

### Data loading (`backend/app/seed_recommendation_data.py`)
`flask seed-recommendations` — idempotent (replaces rows by `Person_ID`, doesn't duplicate on
re-run, verified by running it twice). Reads both xlsx files with `pandas`/`openpyxl` directly from
`datasets/recommendations/` (moved there from repo root, following the existing `datasets/`
convention — not gitignored, unlike the body-image dataset, since these are synthetic tabular
records with no personal-data/license concerns and are small enough to commit, ~140KB each). Loaded
2,000 + 2,000 real rows into the real database; confirmed zero orphaned workout rows.

### KNN training + inference (`ai_model/recommendation/`)
- **`encoding.py`** — shared feature encoding (Age raw, Gender binary 0/1 with a 0.5 fallback for
  unrecognized values, BMI_Category ordinal Thin=0/Normal=1/Overweight=2/Obese=3), imported by both
  training and inference so the query vector is built identically to the training vectors — same
  principle as `opencv_pipeline.py` being shared between CNN training and inference.
- **`train_recommender.py`** — reads `Sri_Lankan_Meal_Dataset_Part_1.xlsx` directly (the workout
  dataset isn't needed for training: it shares the same `Person_ID`/Age/Gender and adds no feature
  signal; the matched workout row is fetched from the DB by `Person_ID` after inference, not
  predicted). Fits a `StandardScaler` + `sklearn.neighbors.NearestNeighbors(n_neighbors=1)`,
  persists both plus the `Person_ID` array via `joblib` to
  `ai_model/saved_models/recommender_<version>.joblib`, with a JSON metadata sidecar and a
  `recommender_active.json` pointer (same versioning spirit as the CNN's `ai_model_files` table, but
  **not** stored in that table — its schema, e.g. `accuracy`, is CNN-specific, and overloading it for
  an unrelated model type would need a discriminator column for no real benefit at this scale).
- **`recommend.py`** — `find_matching_person(body_type_label, age, gender) -> Person_ID`. The CNN
  only ever predicts `thin`/`normal`/`overweight` (`CLASS_NAMES` in `model_architecture.py`) — the
  ordinal encoder's `obese` value only ever appears on the training side, never as a query value.
  Caches the loaded bundle in memory, same pattern as `predict.py`'s model cache.
- Trained on the real 2,000-row dataset; spot-checked three queries against the real DB afterward —
  each match's age/gender/bmi_category matched the query exactly (see verification below).

### Backend wiring (`backend/app/`)
- **`ml_recommendation.py`** — the second (and only other) narrow bridge into `ai_model/` code,
  mirroring `ai_inference.py`: one function, deferred-imported so `joblib`/`sklearn` only load when
  actually matching.
- **`recommendation_service.py`** — split into `match_recommendation()` (read-only: resolves the
  nearest `Person_ID`, validates both its rows exist, raises without writing anything if the
  recommender or a matched row is missing) and `save_recommendation()` (persists the match once an
  `ImageAnalysisRecord` exists). This split matters: `image_analysis_service.analyze()` now calls
  `match_recommendation()` **before** creating the `ImageAnalysisRecord`, so a bad match can never
  leave an orphaned analysis row with no recommendation — the same "validate everything before the
  first write" contract the existing body-type lookup already followed. Verified with a dedicated
  test (`test_analyze_returns_503_and_creates_no_orphaned_analysis_when_recommender_missing`).
- BMI value stored on the recommendation prefers the user's own profile BMI (height/weight, both
  optional fields) when set, falling back to the matched candidate's own BMI otherwise — documented
  in `recommendation_service._resolve_bmi_value`.
- **`recommendation_schema.py`** rewritten: the dashboard endpoint now returns the full matched meal
  record (breakfast/snacks/lunch/dinner/daily_calories) and workout record
  (type/category/intensity/duration/target_muscle/equipment/goal/warmup/cooldown), not the old
  minimal plan-code summary. `matched_workout_record` isn't a real ORM relationship (no direct FK
  column on `user_recommendations` — only `matched_person_id`), so it's attached transiently in the
  controller before the schema dumps it.

### Frontend (`frontend/src/pages/Dashboard.jsx`)
"Body type & latest plan" replaced with "Your personalized plan" — a two-column card showing the
full meal plan (calories badge + breakfast/snacks/lunch/dinner) and full workout plan (type/
intensity/calories badges + category/duration/schedule/target muscle/equipment/goal), plus a body
type + BMI badge in the header. Also refreshed stale Module-10-era copy ("coming in a future
update", a disabled "coming soon" button) that hadn't been updated when Module 10 actually shipped
image analysis.

## How to test locally

**Backend**
```
cd backend
pytest                        # 58 passed
flake8 .                      # clean
flask db upgrade              # applies the Module 11 migration + engine fix
flask seed-recommendations    # loads the 2,000+2,000 real rows
flask run
```

**AI model**
```
cd ai_model
pytest                                    # 40 passed
python recommendation/train_recommender.py   # trains on the real dataset
```

**Frontend**
```
cd frontend
npm run lint     # 0 errors, 1 pre-existing benign warning (unrelated to this module)
npm run build    # succeeds
npm run dev      # log in, set height/weight in profile, upload a photo at /analyze, check /dashboard
```

## Verification performed this session

- 58/58 backend pytest passing (2 new: a successful analyze creates a `UserRecommendation` with the
  right `matched_person_id`; a missing recommender returns 503 and leaves zero orphaned
  `image_analysis_records` rows). 40/40 ai_model pytest passing (8 new: gender/BMI-category encoding
  edge cases, training writes a correct bundle+metadata+active pointer, and — the important one —
  three deliberately well-separated synthetic records where each query's nearest neighbor is
  verified to be the *correct* one, not just *a* one). `flake8`/`black` clean on backend; ai_model's
  pre-existing `E501` line-length noise (no `.flake8` config there, defaults to 79 vs. black's 88) is
  unchanged from before this module and not CI-enforced (`backend-ci.yml` only lints `backend/`).
- Migration applied against real local MySQL; re-verified via direct `information_schema` queries
  that every table is now InnoDB and every declared FK is now actually enforced (see the storage
  engine section above).
- Seeded the real 2,000+2,000 rows twice in a row to confirm idempotency (row counts identical, no
  duplicates). Trained the real KNN model on the real dataset; three spot-check queries
  (`normal`/25/male, `overweight`/60/female, `thin`/18/female) each returned a `Person_ID` whose
  actual DB row matched the query's age/gender/bmi_category exactly.
- **Full real-stack browser verification** (Playwright, headless): registered a new user against the
  real backend + real MySQL, set profile height/weight, uploaded a photo at `/analyze`, confirmed the
  classification result, then loaded `/dashboard` and confirmed the full meal plan (breakfast through
  dinner) and workout plan (target muscle, equipment, etc.) rendered correctly — screenshots reviewed
  directly for both the pre-analysis empty state and the post-analysis populated state. Cross-checked
  the resulting `user_recommendations` row directly in MySQL: correct `matched_person_id`, and
  `bmi_value` matched the profile-derived BMI (not the matched candidate's BMI, confirming the
  "prefer the user's real profile BMI" fallback logic worked as designed).

## Deferred / known limitations

- The CNN's known proof-of-concept weakness (Module 9) now visibly propagates into recommendations:
  in the browser verification above, a plain placeholder test photo was classified `Overweight` by
  the CNN despite the user's real profile BMI being 23.7 (Normal weight) — the dashboard correctly
  shows both (an "Overweight" plan badge alongside the real BMI value), which is expected given the
  CNN's documented status, not a Module 11 defect. Retraining the CNN (deferred, per Module 9/10
  reports) will directly improve recommendation quality too, since the KNN match depends on the
  CNN's label.
- `meal_plans`/`workout_plans` (the original Module 2 template tables) and their seed data are kept,
  unused by the live pipeline now — not deleted, since Modules 12/13's scope for that data isn't
  decided yet.
- The KNN recommender has no admin-facing retrain trigger (matches Module 14's stated scope: "no CNN
  retraining required" — extended here to mean no recommender retraining either; both are offline,
  manually-run scripts).

## Next

Module 12 — Meal plan module: Sri Lankan food data, meal plan detail pages, nutrition breakdown.
