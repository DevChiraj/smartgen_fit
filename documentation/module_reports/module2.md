# Module 2 — Database Schema

**Status:** Complete
**Branch:** `feature/module-2-database-schema` → `dev`

## What was built

### SQLAlchemy models (`backend/app/models/`, one file per entity)
All 10 tables from `SYSTEM.md` §4:

| Model | Table | Notes |
|---|---|---|
| `User` | `users` | unique `email`/`username`, `created_at`/`updated_at` via `TimestampMixin` |
| `BodyTypeCategory` | `body_type_categories` | Thin/Normal/Overweight |
| `BMICategory` | `bmi_categories` | Underweight/Normal/Overweight/Obese ranges |
| `AgeGroup` | `age_groups` | Teenager/Adult/Senior bands |
| `MealPlan` | `meal_plans` | FKs to body type/BMI/age group + `gender`; **unique constraint** on that 4-column lookup combo |
| `WorkoutPlan` | `workout_plans` | same lookup-combo unique constraint |
| `SriLankanFood` | `sri_lankan_foods` | nutrition lookup |
| `ImageAnalysisRecord` | `image_analysis_records` | FK to user + predicted body type, `confidence_score` |
| `UserRecommendation` | `user_recommendations` | links a user's analysis to the meal/workout plan that was looked up |
| `AIModelFile` | `ai_model_files` | model version registry, `is_active` flag |

`app/models/mixins.py` holds the shared `TimestampMixin` / `utcnow()` helper. `app/models/__init__.py` imports every model so Alembic autogenerate and `db.create_all()` see the full metadata.

Relationships are wired both directions (e.g. `MealPlan.body_type` ↔ `BodyTypeCategory.meal_plans`) so lookups and joins work naturally from either side.

### Migrations (Alembic via Flask-Migrate)
- `backend/migrations/` initialized; `env.py` pulls the DB URL from the live Flask app config at runtime (no hardcoded credentials).
- One migration: `1f8f38eaa060_initial_schema_...py` — creates all 10 tables, indexes, and the two composite unique constraints. Autogenerate detected every table correctly on the first pass.
- Verified **upgrade and downgrade both ways** (`flask db upgrade`, `flask db downgrade base`, `flask db upgrade` again) against a throwaway local SQLite file — no real MySQL server is available in this environment (confirmed back in Module 1; `/api/health/db` still correctly reports `503`).

### Seed script (`backend/app/seed.py`)
- `flask seed` CLI command, idempotent (checks-then-creates, safe to run repeatedly — verified by running it twice and confirming row counts didn't change).
- Populates: 3 body types, 4 BMI categories, 3 age groups, 12 Sri Lankan foods, 6 sample meal plans, 6 sample workout plans (one Thin/Normal/Overweight × male/female pair at the Adult age group — a representative subset, not the full combinatorial matrix, per the roadmap's "a few meal/workout plans").
- Nutrition figures and food data are manually curated (flagged per `CLAUDE.md` rule 6 — this isn't the Kaggle-sourced dataset Module 8/12 will bring in, just enough real-shaped data to build and test against).

### Tests (`backend/tests/`)
- `conftest.py`: `app`/`db` fixtures — spins up an in-memory SQLite schema per test via `db.create_all()`/`drop_all()`.
- `test_models.py`: unique-email constraint, meal-plan lookup-combo unique constraint, relationship traversal.
- `test_seed.py`: seed produces the expected row counts; running it twice is a no-op (idempotency).
- 7/7 tests passing; `flake8` clean.

## How to test locally

```
cd backend
.venv/Scripts/activate
pip install -r requirements.txt          # picks up Flask-Migrate/Alembic (already listed since Module 1)
pytest                                    # 7 passed
flake8 .                                  # clean

# Point at your MySQL instance (backend/.env, from .env.example) then:
flask db upgrade                          # creates all 10 tables
flask seed                                # populates reference data + sample plans/foods
```

## Deferred / notes

- **Not verified against real MySQL** — no MySQL server is available in this environment. The migration and seed were verified end-to-end (upgrade, downgrade, re-upgrade, seed, re-seed, constraint enforcement) against a throwaway local SQLite file instead. SQLite and MySQL structural DDL are close enough for this schema (no MySQL-specific types used), but please run `flask db upgrade` against your actual MySQL instance before Module 3 to confirm — flag it back if anything differs.
- Only a representative subset of meal/workout plan combinations is seeded (6 of the possible 3×4×3×2=72). The `RecommendationService` (Module 11) will need a defined fallback for combinations with no seeded plan — worth deciding then, not blocking now.
- `ai_model_files` and `image_analysis_records`/`user_recommendations` tables exist but are empty — populated starting Module 9/10/11.

## Next

Module 3 — Auth: register (with age/validation rules), login, JWT issuing/refresh, bcrypt hashing, protected-route decorator; frontend Login/Register pages wired to `AuthContext`.
