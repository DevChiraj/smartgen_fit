# SYSTEM.md — SmartGen Fit

**AI-Powered Personalized Nutrition and Fitness Recommendation System**
Final Year Project — System Architecture & Development Reference

---

## 1. Project Overview

SmartGen Fit is a full-stack web application that classifies a user's body type from an uploaded full-body image using a CNN, then retrieves a **predefined, rule-based** meal plan and workout schedule from a MySQL database. The AI component is strictly limited to image classification (Thin / Normal / Overweight). No AI is used to generate meal plans, workout plans, or health advice — all recommendations come from static database records selected via simple lookup rules.

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
   ├── Services                   → business logic (recommendation rules, BMI calc, auth)
   ├── Repositories                → DB access (query building via SQLAlchemy)
   ├── Models                     → SQLAlchemy ORM entities
   ├── AI Module                  → preprocessing + CNN inference (called by a service, not a route)
   └── Utilities                  → validators, hashing, JWT helpers, logging, file handling
   │
   ▼
MySQL Database
```

**Request flow example (image analysis):**
`React upload form → POST /api/image-analysis → route → controller → ImageAnalysisService → (OpenCV preprocessing → CNN inference) → RecommendationService → MealPlanRepository / WorkoutPlanRepository → MySQL → JSON response → React dashboard`

The AI module is deliberately isolated behind `ImageAnalysisService`. It returns only a label (`thin` / `normal` / `overweight`) and a confidence score — it never touches meal/workout data. The `RecommendationService` is a separate, pure rule-based component that takes `(body_type, bmi_category, age_group, gender)` and queries the database. This separation is a hard project rule, not just a convenience — it keeps the AI boundary auditable.

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
│   └── saved_models/               # versioned .h5 / SavedModel files
├── datasets/
│   ├── body_images/                # Kaggle or manually curated, class-labeled subfolders
│   └── sri_lankan_foods/           # CSV nutrition data
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

**meal_plans**
`meal_plan_id (PK), plan_code, body_type_id (FK), bmi_category_id (FK), age_group_id (FK), gender, breakfast, lunch, dinner, snacks, calories, protein_g, carbs_g, fat_g, fiber_g, vitamins, minerals, daily_water_ml`

**workout_plans**
`workout_plan_id (PK), plan_code, body_type_id (FK), bmi_category_id (FK), age_group_id (FK), gender, warm_up, cardio, strength_training, stretching, cool_down, duration_minutes, repetitions, weekly_schedule, calories_burned`

**sri_lankan_foods**
`food_id (PK), food_name, category, calories, protein_g, carbs_g, fat_g, fiber_g, vitamins, minerals, image_url`

**image_analysis_records**
`analysis_id (PK), user_id (FK), image_path, predicted_body_type_id (FK), confidence_score, created_at`

**user_recommendations** *(drives the "Latest Meal/Workout Plan" dashboard widgets)*
`recommendation_id (PK), user_id (FK), analysis_id (FK), meal_plan_id (FK), workout_plan_id (FK), bmi_value, created_at`

**ai_model_files**
`model_id (PK), version, file_path, accuracy, trained_date, is_active`

Relationships: `meal_plans`/`workout_plans` are looked up by the composite of `(body_type_id, bmi_category_id, age_group_id, gender)` — this composite should be indexed (or unique-constrained if every combination maps to exactly one plan).

---

## 5. API Structure (REST, versioned under `/api/v1`)

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Create account, validate age ≥ 15, hash password |
| POST | `/auth/login` | Issue JWT |
| GET/PUT | `/users/me` | View/edit profile |
| POST | `/users/me/profile-picture` | Upload profile image |
| POST | `/bmi/calculate` | BMI + category (stateless utility) |
| POST | `/image-analysis` | Upload image → CNN classification → triggers recommendation |
| GET | `/image-analysis/history` | Past analyses for the user |
| GET | `/recommendations/latest` | Latest meal + workout plan for dashboard |
| GET | `/meal-plans/:id`, `/workout-plans/:id` | Plan detail |
| GET | `/foods` | Sri Lankan food/nutrition lookup |
| CRUD | `/admin/users`, `/admin/meal-plans`, `/admin/workout-plans`, `/admin/foods`, `/admin/body-types`, `/admin/bmi-categories` | Admin management, JWT role-guarded |

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
       → Result stored in image_analysis_records
       → RecommendationService (pure DB lookup, no AI) → meal_plan + workout_plan
```

Dataset strategy: search Kaggle for body-type/silhouette classification datasets first; if coverage is incomplete, supplement with a manually curated, clearly-labeled dataset so training isn't blocked. Same approach for Sri Lankan food nutrition data — Kaggle first, manual CSV fallback. The CNN is trained offline (`ai_model/training/`) and the backend only loads the exported model file for inference — training is never triggered from a request.

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
11. Recommendation engine (rule-based lookup service)
12. Meal plan module (frontend + backend + Sri Lankan food data)
13. Workout plan module (frontend + backend)
14. Admin panel (CRUD for all managed entities)
15. Swagger documentation pass
16. Testing (backend unit/integration, frontend component tests)
17. Final review, deployment docs, polish

## 10. Implementation Strategy

- Generate **one module at a time**, fully production-ready (code + brief explanation), then stop and wait for confirmation before continuing — no bundling of modules.
- Every module includes: the code, where it sits in the folder structure, and how to test it locally.
- Datasets: attempt Kaggle first; if gaps exist, generate realistic manual data rather than blocking progress, and clearly flag it as manually-sourced.
- Never let the AI module leak into recommendation logic — enforced by keeping `ai_model/` and `RecommendationService` fully decoupled (label in, plan out, no shared code path).

## 11. Project Rules (hard constraints)

- AI performs **only** image classification (Thin/Normal/Overweight) — never generates meal plans, workouts, calories, or health advice.
- All recommendations are predefined records retrieved by rule-based DB lookup on Body Type + BMI Category + Age Group + Gender.
- Minimum registration age: 15. Passwords hashed (bcrypt), never stored/logged in plaintext.
- Admins can manage meal/workout/food data without ever retraining or redeploying the CNN.
- No module's code is generated until the prior module is confirmed by the project owner.

---

*Next step: review this document. Once approved, Module 1 (project scaffolding) will be generated.*
