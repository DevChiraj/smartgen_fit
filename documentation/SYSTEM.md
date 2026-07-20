# SYSTEM.md — SmartGen Fit

**AI-Powered Personalized Nutrition and Fitness Recommendation System**
Final Year Project — System Architecture & Development Reference

---

## 1. Project Overview

SmartGen Fit is a full-stack web application that classifies a user's body type from an uploaded full-body image using a CNN, then matches the user to a similar real record in a Sri Lankan meal + workout dataset (via a K-Nearest-Neighbors model) and returns that record's meal plan and workout schedule from a MySQL database. The AI component is strictly limited to image classification (Thin / Normal / Overweight) and to similarity matching. No AI generates meal plans, workout plans, or health advice at request time — a KNN match always resolves to an existing, real database row, read and returned as-is. *(Module 11 replaced the original hand-written composite-key lookup table with this similarity-matched approach over a 2,000-row real dataset — see `documentation/module_reports/module11.md`.)*

**Stack**
| Layer | Technology |
|---|---|
| Frontend | React.js, Bootstrap 5 / Material UI |
| Backend | Python Flask (REST API) |
| Database | MySQL, SQLAlchemy ORM |
| AI/CV | TensorFlow, Keras, OpenCV, CNN |
| Auth | JWT, Bcrypt |
| Docs | Swagger (Flask-RESTX or Flasgger) |
| Dev Env | Visual Studio Code |

---

## 2. Architecture

MVC + layered service architecture on the backend, component-based SPA on the frontend.

```
Client (React SPA)
   │  HTTPS / JSON
   ▼
Flask REST API
   │
   ├── Routes (Blueprints)        → HTTP endpoints only, no logic
   ├── Controllers                → request/response orchestration
   ├── Services                   → business logic (recommendation matching, BMI calc, auth)
   ├── Repositories                → DB access (query building via SQLAlchemy)
   ├── Models                     → SQLAlchemy ORM entities
   ├── AI Module                  → preprocessing + CNN inference + KNN recommendation matching (called by a service, not a route)
   └── Utilities                  → validators, hashing, JWT helpers, logging, file handling
   │
   ▼
MySQL Database
```

**Request flow example (image analysis):**
`React upload form → POST /api/image-analysis → route → controller → ImageAnalysisService → (OpenCV preprocessing → CNN inference) → RecommendationService.match_recommendation() → (KNN match via ai_model/recommendation/) → MealRecommendationRecord / WorkoutRecommendationRecord lookup by Person_ID → RecommendationService.save_recommendation() → MySQL → JSON response → React dashboard`

The AI module is deliberately isolated behind two narrow bridges: `app/ai_inference.py` (CNN classification) and `app/ml_recommendation.py` (KNN matching). `ai_inference.py` returns only a label (`thin` / `normal` / `overweight`) and a confidence score — it never touches meal/workout data. `ml_recommendation.py` takes `(predicted_body_type, age, gender)` and returns only a `Person_ID` — it never touches the database and has no idea what a meal plan looks like. `RecommendationService` is the only component that bridges the two: it calls `ml_recommendation.py` for a `Person_ID`, then reads that candidate's real row from `meal_recommendation_records` / `workout_recommendation_records` via ordinary repository queries. Nothing about the recommended content is generated, invented, or interpolated — it's always an existing dataset row, selected by nearest-neighbor distance instead of an exact composite key. This separation (classify → match → look up, each step decoupled and independently testable) is a hard project rule, not just a convenience — it keeps the AI boundary auditable.

---

## 3. Folder Structure

```
smartgen-fit/
├── SYSTEM.md
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/          # reusable UI (Navbar, Footer, Card, ChartWidget, etc.)
│       ├── pages/                # LandingPage, Login, Register, Dashboard, BMICalculator,
│       │                         # ImageAnalysis, MealPlan, WorkoutPlan, Profile, Admin/*
│       ├── layouts/              # PublicLayout, AuthenticatedLayout, AdminLayout
│       ├── services/             # axios API clients (authService.js, userService.js, ...)
│       ├── context/              # AuthContext (JWT/session state)
│       ├── hooks/
│       ├── utils/                # validators, formatters
│       ├── assets/               # images, icons
│       └── styles/
├── backend/
│   ├── app/
│   │   ├── __init__.py           # app factory
│   │   ├── config.py              # env-based config classes
│   │   ├── extensions.py          # db, jwt, bcrypt, cors init
│   │   ├── routes/                # Blueprints: auth, users, bmi, image_analysis,
│   │   │                          # meal_plans, workout_plans, foods, admin
│   │   ├── controllers/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── models/                # SQLAlchemy models, one file per entity
│   │   ├── schemas/                # request/response validation (marshmallow or pydantic)
│   │   ├── utils/                  # validators.py, security.py, logger.py, file_handler.py
│   │   └── docs/                   # Swagger config
│   ├── migrations/                 # Alembic
│   ├── tests/
│   └── run.py
├── ai_model/
│   ├── notebooks/                  # EDA, training experiments
│   ├── training/                   # train.py, model_architecture.py, data_generator.py
│   ├── inference/                  # predict.py — loaded by backend service
│   ├── preprocessing/              # opencv_pipeline.py (resize, crop, normalize)
│   ├── recommendation/             # train_recommender.py, recommend.py, encoding.py — KNN match (Module 11)
│   └── saved_models/               # versioned .h5/.keras CNN files + recommender_*.joblib bundles
├── datasets/
│   ├── body_images/                # Kaggle or manually curated, class-labeled subfolders
│   ├── sri_lankan_foods/           # Kaggle nutrition dataset (Module 12), 119 real foods
│   ├── recommendations/            # Sri Lankan meal + workout xlsx datasets (Module 11), joined by Person_ID
│   └── workouts/                   # Kaggle exercise dataset (Module 13), 50 real exercises
├── uploads/                        # runtime user-uploaded images (gitignored)
└── documentation/
    ├── SYSTEM.md (copy)
    ├── api_spec.md
    ├── er_diagram.png
    └── module_reports/
```

---

## 4. Database Design (MySQL)

**users**
`user_id (PK), full_name, date_of_birth, age, gender, email (unique), phone_number, height_cm, weight_kg, username (unique), password_hash, profile_picture_url, role (user/admin), created_at, updated_at`

**body_type_categories**
`body_type_id (PK), name (Thin/Normal/Overweight), description`

**bmi_categories**
`bmi_category_id (PK), category_name, min_bmi, max_bmi`

**age_groups** *(reference table, or enum in code)*
`age_group_id (PK), name (Teenager 15-19 / Adult 20-59 / Senior 60+), min_age, max_age`

**meal_plans** *(legacy — the original Module 2 template table; not exposed via any API endpoint, see §5)*
`meal_plan_id (PK), plan_code, body_type_id (FK), bmi_category_id (FK), age_group_id (FK), gender, breakfast, lunch, dinner, snacks, calories, protein_g, carbs_g, fat_g, fiber_g, vitamins, minerals, daily_water_ml`

**workout_plans** *(legacy — same status as `meal_plans`)*
`workout_plan_id (PK), plan_code, body_type_id (FK), bmi_category_id (FK), age_group_id (FK), gender, warm_up, cardio, strength_training, stretching, cool_down, duration_minutes, repetitions, weekly_schedule, calories_burned`

**sri_lankan_foods** *(Module 12 — 119 rows loaded from `datasets/sri_lankan_foods/SrilankanCommonFoods.xlsx`, a real Kaggle dataset replacing the original 12-row manual placeholder)*
`food_id (PK), food_name, category, serving_size, calories, protein_g, carbs_g, fat_g, fiber_g (nullable), vitamins (nullable), minerals (nullable), image_url (nullable)` — the Kaggle source has no category/fiber/vitamin/mineral/image columns; `category` is assigned via an explicit per-food mapping in `backend/app/seed_food_data.py` (auditable, not keyword heuristics), the rest are left null rather than invented.

**exercises** *(Module 13 — 50 rows loaded from `datasets/workouts/Top50ExercisesForYourBody.csv`, a real Kaggle dataset; a standalone exercise reference library, unrelated to the Module 11 KNN pipeline or the legacy `workout_plans` table)*
`exercise_id (PK), exercise_name, target_muscle, difficulty (Beginner/Intermediate/Advanced), equipment (nullable), sets, reps, calories_per_30min, benefit`

**image_analysis_records**
`analysis_id (PK), user_id (FK), image_path, predicted_body_type_id (FK), confidence_score, created_at`

**meal_recommendation_records** *(Module 11 — the KNN candidate pool, 2,000 rows loaded from `datasets/recommendations/Sri_Lankan_Meal_Dataset_Part_1.xlsx` via `flask seed-recommendations`)*
`record_id (PK), person_id (unique, indexed), age, gender, height_cm, weight_kg, bmi, bmi_category, breakfast, morning_snack, lunch, evening_snack, dinner, daily_calories`

**workout_recommendation_records** *(Module 11 — same dataset pairing, 2,000 rows loaded from `Workout_Dataset_Matched_Advanced.xlsx`; `person_id` is a real FK into `meal_recommendation_records`, verified 1:1 with no orphans on either side)*
`record_id (PK), person_id (FK → meal_recommendation_records.person_id, unique, indexed), age, gender, fitness_level, workout_type, workout_category, intensity, duration_min, days_per_week, calories_burned, target_muscle, equipment, indoor_outdoor, goal, warmup_min, cooldown_min`

**user_recommendations** *(drives the "Your personalized plan" dashboard widget)*
`recommendation_id (PK), user_id (FK), analysis_id (FK), meal_plan_id (FK, nullable — legacy template-plan column, unused since Module 11), workout_plan_id (FK, nullable — same), matched_person_id (FK → meal_recommendation_records.person_id, nullable), bmi_value, created_at`

**ai_model_files**
`model_id (PK), version, file_path, accuracy, trained_date, is_active` — CNN models only. The Module 11 KNN recommender bundle is *not* registered here (its schema, e.g. `accuracy`, is CNN-specific); it's tracked by a filesystem pointer instead — see §6.

Relationships: `meal_plans`/`workout_plans` (the original Module 2 template tables) are still looked up by the composite of `(body_type_id, bmi_category_id, age_group_id, gender)`, but `image_analysis_service.analyze()` no longer creates rows through that path — every new `user_recommendations` row is populated via the Module 11 KNN match instead, using `matched_person_id` to join `meal_recommendation_records` / `workout_recommendation_records`. The old columns/tables are kept for backward compatibility, not deleted. **Module 12 decision:** since no live flow ever populates a `meal_plans`/`workout_plans` row anymore, Module 12 does not build detail endpoints for them (the `/meal-plans/:id`/`/workout-plans/:id` endpoints once planned here are dropped from §5) — building a page around permanently-empty user data would be dead surface area. `sri_lankan_foods`/`exercises` are unrelated to this and *are* fully wired up (§5), since both are independent public reference data, not part of the matching pipeline.

**Module 13 note on "weekly schedule":** neither `workout_recommendation_records` (live) nor the legacy `workout_plans.weekly_schedule` string (dead) has any real per-day-of-week data — `workout_recommendation_records` only has a `days_per_week` integer count. The frontend's "suggested weekly schedule" (`frontend/src/utils/weeklySchedule.js`) deterministically spreads that count across a 7-day grid and is explicitly labeled as a suggestion, not sourced data — see `module13.md`.

---

## 5. API Structure (REST, versioned under `/api/v1`)

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Create account, validate age ≥ 15, hash password |
| POST | `/auth/login` | Issue JWT |
| GET/PUT | `/users/me` | View/edit profile |
| POST | `/users/me/profile-picture` | Upload profile image |
| POST | `/bmi/calculate` | BMI + category (stateless utility) |
| POST | `/image-analysis` | Upload image → CNN classification → KNN match → triggers recommendation |
| GET | `/image-analysis/history` | Past analyses for the user |
| GET | `/recommendations/latest` | Latest matched meal + workout record (full detail) for dashboard |
| GET | `/foods` | Sri Lankan food/nutrition list — `?category=`, `?q=` filters (public, no auth) |
| GET | `/foods/categories` | Distinct food categories, for the filter dropdown (public) |
| GET | `/foods/:id` | Single food's full nutrition detail (public) |
| GET | `/exercises` | Exercise library list — `?difficulty=`, `?q=` filters (public, no auth) |
| GET | `/exercises/difficulties` | Distinct difficulty levels, for the filter dropdown (public) |
| GET | `/exercises/:id` | Single exercise's full detail (public) |
| GET/PUT/DELETE | `/admin/users`, `/admin/users/:id` | List/update (role, profile)/delete users — role="admin" required |
| POST/PUT/DELETE | `/admin/foods`, `/admin/foods/:id` | Full CRUD on `sri_lankan_foods` (reads stay on the public `/foods` endpoints) — admin only |
| POST/PUT/DELETE | `/admin/exercises`, `/admin/exercises/:id` | Full CRUD on `exercises` (reads stay on the public `/exercises` endpoints) — admin only |
| GET/PUT | `/admin/body-types`, `/admin/body-types/:id` | List/update — description only, `name` is fixed (see §11) — admin only |
| GET/POST/PUT/DELETE | `/admin/bmi-categories`, `/admin/bmi-categories/:id` | Full CRUD on BMI category thresholds — admin only |

Swagger docs generated via Flasgger/Flask-RESTX, served at `/api/docs`.

---

## 6. AI Workflow

```
Upload → Validation (type/size/dimensions)
       → Preprocessing (resize, normalize, denoise)
       → OpenCV Processing (contrast/lighting normalization)
       → Body Detection (bounding box / silhouette isolation)
       → Feature Extraction (CNN backbone feature maps)
       → CNN Classification → {Thin, Normal, Overweight} + confidence
       → RecommendationService.match_recommendation(user, predicted_label)
             → KNN match (ai_model/recommendation/recommend.py) on
               [age, gender, predicted body type] → nearest Person_ID
             → meal_recommendation_records / workout_recommendation_records
               looked up by that Person_ID (validated to exist first)
       → Result stored in image_analysis_records
       → RecommendationService.save_recommendation() → user_recommendations
         (matched_person_id, bmi_value) — no AI or lookup happens after this point,
         the dashboard just reads back what was already matched
```

Dataset strategy: search Kaggle for body-type/silhouette classification datasets first; if coverage is incomplete, supplement with a manually curated, clearly-labeled dataset so training isn't blocked. Same approach for Sri Lankan food nutrition data — Kaggle first, manual CSV fallback. The CNN is trained offline (`ai_model/training/`) and the backend only loads the exported model file for inference — training is never triggered from a request.

**KNN recommender (Module 11):** trained offline via `ai_model/recommendation/train_recommender.py` directly from `datasets/recommendations/Sri_Lankan_Meal_Dataset_Part_1.xlsx` (Age/Gender/BMI_Category/Person_ID — the workout dataset shares the same Person_ID/Age/Gender so it isn't needed for training, only for the post-match DB lookup). Features: Age (raw), Gender (binary-encoded), BMI_Category (ordinal: Thin/Underweight=0, Normal=1, Overweight=2, Obese=3) — the CNN's predicted label is mapped onto that same ordinal scale at inference time (it never predicts "Obese", since `CLASS_NAMES` is Thin/Normal/Overweight only). `StandardScaler` + `sklearn.neighbors.NearestNeighbors(n_neighbors=1)`, persisted via `joblib` to `ai_model/saved_models/recommender_<version>.joblib`, with a `recommender_active.json` pointer file (analogous to `ai_model_files.is_active`, but filesystem-based since this model type isn't in that table). Re-run `train_recommender.py` any time the dataset changes; `flask seed-recommendations` reloads the DB candidate pool independently (idempotent, replaces rows by Person_ID).

---

## 7. Coding Standards

- **Python:** PEP8, type hints, docstrings on services/repositories, `black` + `flake8`.
- **React:** functional components + hooks, ESLint + Prettier, one component per file, PropTypes or TypeScript-style JSDoc.
- **Naming:** `snake_case` (Python/DB), `camelCase` (JS), `PascalCase` (React components/classes).
- **Errors:** centralized Flask error handlers returning consistent JSON `{error, message, status}`; React error boundaries + toast notifications.
- **Logging:** Python `logging` module to rotating file handler, request IDs, no sensitive data (passwords, tokens) in logs.
- **Validation:** all inputs validated server-side (schemas) regardless of frontend validation.

## 8. Git Workflow

- `main` (stable/deployable), `dev` (integration), `feature/<module-name>` branches.
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- One module = one feature branch = one PR into `dev`, merged after the module is confirmed working.
- Tag releases (`v0.1.0`, …) at major milestones.

---

## 9. Development Roadmap (module-by-module, one module per session)

1. Project scaffolding (backend app factory, frontend CRA/Vite init, config, folder structure, DB connection)
2. Database schema + SQLAlchemy models + Alembic migrations + seed data
3. Authentication module (register, login, JWT, bcrypt, age validation)
4. User profile management (view/edit, profile picture upload)
5. Landing page + public navigation (frontend)
6. BMI Calculator module
7. Dashboard module (profile, BMI, body type, latest plans, charts, quick actions)
8. AI dataset preparation (Kaggle sourcing / manual curation, preprocessing scripts)
9. CNN training pipeline + model export
10. Image analysis module (upload, OpenCV pipeline, inference API, history)
11. Recommendation engine (KNN similarity-match service — amended from the original rule-based lookup, see §11)
12. Meal plan module (frontend + backend + Sri Lankan food data)
13. Workout plan module: exercise reference library (frontend + backend) + suggested weekly schedule for the user's matched plan
14. Admin panel: CRUD for users, foods, exercises, body types (description only), BMI categories — no CRUD for the legacy `meal_plans`/`workout_plans` tables (dead since Module 11, same reasoning as Modules 12/13)
15. Swagger documentation pass
16. Testing (backend unit/integration, frontend component tests)
17. Final review, deployment docs, polish

## 10. Implementation Strategy

- Generate **one module at a time**, fully production-ready (code + brief explanation), then stop and wait for confirmation before continuing — no bundling of modules.
- Every module includes: the code, where it sits in the folder structure, and how to test it locally.
- Datasets: attempt Kaggle first; if gaps exist, generate realistic manual data rather than blocking progress, and clearly flag it as manually-sourced.
- Never let the AI module leak into recommendation logic — enforced by keeping `ai_model/` and `RecommendationService` fully decoupled (label in, plan out, no shared code path).

## 11. Project Rules (hard constraints)

- AI performs **only** image classification (Thin/Normal/Overweight) and, since Module 11, similarity matching (KNN) — neither one generates meal plans, workouts, calories, or health advice as free text. Every recommendation the user sees is an existing, real row read verbatim from `meal_recommendation_records` / `workout_recommendation_records`.
- **(Amended in Module 11 — project owner's explicit decision, see `documentation/module_reports/module11.md`.)** Recommendations are no longer a simple 4-key rule-based lookup. A KNN model matches (predicted body type, age, gender) against a 2,000-row real dataset and returns the nearest candidate's `Person_ID`; that candidate's own meal + workout row is then read from the DB unmodified. This is still not generative — nothing is invented at request time — but it replaces the original small hand-written template table with a much larger dataset and a similarity match instead of an exact key.
- Minimum registration age: 15. Passwords hashed (bcrypt), never stored/logged in plaintext.
- Admins can manage meal/workout/food data without ever retraining or redeploying the CNN. (The KNN recommender is a separate offline training step, same principle — see §6.) **Module 14** delivers this as CRUD over `sri_lankan_foods`/`exercises`/`bmi_categories` (full CRUD) and `body_type_categories` (description only — `name` is fixed since it keys `image_analysis_service`'s classification lookup directly against the CNN's `CLASS_NAMES`). There is no admin CRUD over `meal_recommendation_records`/`workout_recommendation_records` (the 2,000-row Module 11 candidate pool) — that's bulk reference data refreshed via `flask seed-recommendations`, not one-off editable content.
- The first admin account is bootstrapped via `flask promote-admin <email>` (CLI only, never an HTTP endpoint — self-service admin escalation is not possible). Every subsequent admin write requires the `admin` role (`role_required`, JWT claim set at login). The admin user-management endpoints refuse to demote/delete the last remaining admin or let an admin delete their own account, to prevent an accidental full lockout.
- No module's code is generated until the prior module is confirmed by the project owner.

---

*Next step: review this document. Once approved, Module 1 (project scaffolding) will be generated.*
