# CLAUDE.md — SmartGen Fit

Read this file, `SYSTEM.md`, and `README.md` at the start of every session, in that order. `SYSTEM.md` is the architecture reference (DB schema, API list, folder structure, AI workflow) — don't duplicate it here, look it up there. This file is the operating contract: the rules that don't change and the checklist of what's left to build.

**Status:** Modules 1-16 complete — see `documentation/module_reports/`. Current target: **Module 17**.

**Standing heads-up:** the Module 9 CNN is a pipeline proof-of-concept only — trained on a 48-image dataset with known label-accuracy issues, kept as-is per explicit supervisor direction (see `module9.md`). It is not fit for real classification. Module 11's KNN recommender consumes that same predicted label as one of its match features, so a wrong CNN prediction now also produces a mismatched meal/workout recommendation — this is expected given the CNN's documented status, not a Module 11 bug. Retrain the CNN on corrected/larger data before treating either its predictions or the recommendations derived from them as meaningful.

**Standing heads-up (MySQL engine):** the local dev MySQL server has `default_storage_engine = MyISAM` (server-level, non-standard) instead of InnoDB — discovered and fixed for all *existing* tables in Module 11, but the server default itself was never changed. **Every new migration that creates a table must pass `mysql_engine='InnoDB'` explicitly to `op.create_table(...)`** (see Module 13's `f2895c49193b_add_exercises_table.py` for the pattern), or the new table silently gets MyISAM again — no foreign keys, no transaction rollback. Check this on every future migration until the server config itself is fixed.

**Standing heads-up (exercise demo GIFs):** the 37 files in `frontend/public/exercise-gifs/` have **unresolved media licensing** — sourced from a community GitHub backup of a Kaggle dataset whose own README disclaims ownership of the actual GIF content ("I do not own any of the content... all rights belong to the original creators and dataset owner"). This was the project owner's explicit, informed choice over a fully-clean-but-static-only alternative (wger.de, CC-BY-SA 4.0) — see `documentation/exercise_demo_gifs_sourcing.md` for the full trade-off, matching methodology, and per-exercise provenance table. Fine for this non-commercial academic project; **must be reviewed/replaced before any commercial deployment or redistribution.**

## Non-negotiable rules

1. **The AI model only classifies body images** (Thin/Normal/Overweight). It must never generate meal plans, workouts, calories, or health advice, and the code path must never let it. `RecommendationService` and `ai_model/` stay decoupled — label in, plan out, nothing shared.
2. **Recommendations are similarity-matched, never generated at request time.** *(Amended in Module 11, project owner's explicit decision — see `module11.md`.)* A KNN model (`ai_model/recommendation/`) matches the CNN's predicted body type + the user's Age/Gender against a fixed 2,000-row candidate pool (`meal_recommendation_records` / `workout_recommendation_records`, loaded from real datasets) and returns an existing candidate's `Person_ID`. The meal/workout content shown to the user is always that candidate's own real row, read straight from the DB — nothing is synthesized, interpolated, or authored by a model at request time. This keeps the spirit of the original rule (no free-text generation, no LLM-authored plans, the boundary stays auditable) while replacing the old small hand-written template table with a much larger real dataset matched by similarity instead of an exact composite key.
3. **One module per session.** Fully build and verify the current module (code + tests), write a short report to `documentation/module_reports/moduleN.md`, then **stop and wait for explicit approval** before starting the next. Don't bundle modules.
4. Minimum registration age is 15, enforced server-side. Passwords are bcrypt-hashed, never logged. No secrets committed — `.env` stays gitignored; only `.env.example` is tracked.
5. All inputs validated server-side regardless of frontend validation.
6. Datasets: try Kaggle first (body images, Sri Lankan food nutrition). If coverage is incomplete, generate a clearly-labeled manual dataset rather than blocking — don't stall the project on missing data.

## Session workflow

1. Check `documentation/module_reports/` to see what's already done.
2. Implement the current module completely — don't leave partial stubs in a "done" module.
3. Verify it actually works: run the relevant tests, hit the endpoint with `curl`, or run the frontend build. Don't report a module complete on code inspection alone.
4. Write `documentation/module_reports/moduleN.md`: what was built, how to test it, anything deferred.
5. Stop. Summarize what's done and what Module N+1 will cover. Wait for the go-ahead.

## Git / CI-CD workflow (standing rule — do this after every piece of work, no need to ask again)

- Branches: `main` (stable, promoted manually by the project owner — never pushed to directly) ← `dev` (integration, always green) ← `feature/<name>` (one per module/task).
- After finishing a module or task: commit on a `feature/<name>` branch, push it, open a PR into `dev` (`gh pr create --base dev`).
- If the change touches `backend/**` or `frontend/**`, the matching GitHub Actions workflow (`.github/workflows/backend-ci.yml` / `frontend-ci.yml`) runs lint + tests/build automatically.
- Auto-merge the PR into `dev` once CI passes (`gh pr merge --auto --squash --delete-branch`; for changes with no matching CI, e.g. docs-only, merge directly since there's nothing to wait on).
- `dev` → `main` is **not** automatic — that promotion is the project owner's call (e.g. at a release tag), per `SYSTEM.md` §8.
- This does not relax rule 3 above: still stop and wait for explicit approval before *starting* the next module. The commit/PR/merge cycle happens for the module just finished, not as permission to keep going.

## Commands

**Backend** (`backend/`): `pip install -r requirements.txt` · `flask run` · `pytest` (add `--cov=app --cov-report=term-missing` for a coverage report) · `flask db migrate -m "message"` / `flask db upgrade` (from Module 2 onward)
**Frontend** (`frontend/`): `npm install` · `npm run dev` · `npm run build` · `npm run lint` · `npm run test` (`npm run test:watch` for watch mode)
**Health check:** `curl localhost:5000/api/health` and `/api/health/db`

## Conventions (full detail in `SYSTEM.md` §7-8)

- Python: PEP8, type hints, docstrings on services/repositories, `black` + `flake8`.
- React: functional components + hooks, one component per file, ESLint + Prettier.
- Naming: `snake_case` (Python/DB), `camelCase` (JS), `PascalCase` (React components).
- Conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`), one feature branch per module, PR into `dev`.
- Centralized error handling: Flask JSON error handlers, React error boundaries + toasts.

## Build roadmap (check items off / delete as completed — keep this list current, not a fossil)

- [x] **Module 1** — Project scaffolding (Flask factory, Vite+React shell, folder structure, health check)
- [x] **Module 2** — Database schema: SQLAlchemy models for every table in `SYSTEM.md` §4, Alembic migrations, seed script with realistic sample data (body types, BMI categories, age groups, a few meal/workout plans, sample foods)
- [x] **Module 3** — Auth: register (with age/validation rules), login, JWT issuing/refresh, bcrypt hashing, protected-route decorator; frontend Login/Register pages wired to `AuthContext`
- [x] **Module 4** — Profile management: view/edit profile, profile picture upload (secure file handling, size/type limits)
- [x] **Module 5** — Public landing page: nav bar (Home/About/Healthy Foods/Workouts/BMI Calculator/Contact/Login/Register), healthcare-themed content per `SYSTEM.md`
- [x] **Module 6** — BMI Calculator (stateless endpoint + frontend widget, category display)
- [x] **Module 7** — Authenticated dashboard: profile summary, BMI, body type, latest meal/workout plan, charts, quick actions
- [x] **Module 8** — AI dataset preparation: source/curate body-image dataset (Kaggle-first), preprocessing scripts in `ai_model/preprocessing/`
- [x] **Module 9** — CNN training pipeline (`ai_model/training/`), export versioned model to `ai_model/saved_models/`, record in `ai_model_files` table
- [x] **Module 10** — Image analysis module: upload → validation → OpenCV preprocessing → CNN inference API → `image_analysis_records`, wired to frontend upload page
- [x] **Module 11** — Recommendation engine: KNN similarity match (Age/Gender/predicted body type) over a 2,000-row Sri Lankan meal + workout dataset pair, triggered after classification, populates `user_recommendations` with a matched `Person_ID`; dashboard shows the full matched meal + workout detail
- [x] **Module 12** — Meal plan module: 119-row real Kaggle Sri Lankan nutrition dataset (`sri_lankan_foods`, replacing the 12-row placeholder), public `/foods` search+category-filter API and Healthy Foods page, authenticated `/meal-plan` detail page for the user's live Module 11 match
- [x] **Module 13** — Workout plan module: 50-row real Kaggle exercise dataset (`exercises`, replacing nothing — no prior workout reference data existed), public `/exercises` search+difficulty-filter API and Workouts page, suggested weekly schedule (derived from `days_per_week`, clearly labeled as a suggestion) added to the `/meal-plan` page
- [x] **Module 14** — Admin panel: `flask promote-admin` CLI bootstrap, role-guarded `/admin/*` API, CRUD for users/foods/exercises/BMI categories, description-only edit for body types (name is fixed — keys the CNN's classification lookup); no CRUD for the legacy `meal_plans`/`workout_plans` tables (dead since Module 11) — no CNN retraining required
- [x] **Module 15** — Swagger docs pass: all 37 endpoints across 9 blueprints documented via Flasgger at `/api/docs`, one YAML spec per endpoint, with a regression test (`test_every_registered_route_is_documented`) that fails if a future route ships undocumented
- [x] **Module 16** — Testing pass: backend coverage audit with `pytest-cov` (94%→99%, 97→137 tests, gap-driven not blind-100%), frontend test framework introduced from scratch (Vitest + RTL, 0→89 tests), both wired into CI (`npm run test` added to `frontend-ci.yml`)
- [ ] **Module 17** — Deployment (see below)

## Module 17 — Deployment (default plan, adjust if you have a preferred host)

- Containerize backend (`Dockerfile`) and add `docker-compose.yml` for backend + MySQL for local/demo parity.
- Suggested low-cost hosting for an FYP demo: backend on Render or Railway, MySQL on Railway/Clever Cloud (or your university's server if required for submission), frontend on Vercel or Netlify.
- Environment variables set via host dashboard, never committed. `SECRET_KEY`/`JWT_SECRET_KEY` regenerated for production (don't reuse dev values).
- Run migrations against the production DB before first deploy (`flask db upgrade`).
- Enable HTTPS (host default certs are fine), lock CORS to the real frontend origin, disable Flask debug mode.
- Smoke-test `/api/health` and `/api/health/db` against the deployed backend before declaring this module done.
- Write final `documentation/module_reports/module17.md` with live URLs and a one-page "how to redeploy" note.
