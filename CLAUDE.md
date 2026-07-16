# CLAUDE.md — SmartGen Fit

Read this file, `SYSTEM.md`, and `README.md` at the start of every session, in that order. `SYSTEM.md` is the architecture reference (DB schema, API list, folder structure, AI workflow) — don't duplicate it here, look it up there. This file is the operating contract: the rules that don't change and the checklist of what's left to build.

**Status:** Module 1 (project scaffolding) is complete — see `documentation/module_reports/module1.md`. Current target: **Module 2**.

## Non-negotiable rules

1. **The AI model only classifies body images** (Thin/Normal/Overweight). It must never generate meal plans, workouts, calories, or health advice, and the code path must never let it. `RecommendationService` and `ai_model/` stay decoupled — label in, plan out, nothing shared.
2. **Recommendations are rule-based DB lookups only** — keyed on Body Type + BMI Category + Age Group + Gender. Never invent a plan at request time.
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

**Backend** (`backend/`): `pip install -r requirements.txt` · `flask run` · `pytest` · `flask db migrate -m "message"` / `flask db upgrade` (from Module 2 onward)
**Frontend** (`frontend/`): `npm install` · `npm run dev` · `npm run build` · `npm run lint`
**Health check:** `curl localhost:5000/api/health` and `/api/health/db`

## Conventions (full detail in `SYSTEM.md` §7-8)

- Python: PEP8, type hints, docstrings on services/repositories, `black` + `flake8`.
- React: functional components + hooks, one component per file, ESLint + Prettier.
- Naming: `snake_case` (Python/DB), `camelCase` (JS), `PascalCase` (React components).
- Conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`), one feature branch per module, PR into `dev`.
- Centralized error handling: Flask JSON error handlers, React error boundaries + toasts.

## Build roadmap (check items off / delete as completed — keep this list current, not a fossil)

- [x] **Module 1** — Project scaffolding (Flask factory, Vite+React shell, folder structure, health check)
- [ ] **Module 2** — Database schema: SQLAlchemy models for every table in `SYSTEM.md` §4, Alembic migrations, seed script with realistic sample data (body types, BMI categories, age groups, a few meal/workout plans, sample foods)
- [ ] **Module 3** — Auth: register (with age/validation rules), login, JWT issuing/refresh, bcrypt hashing, protected-route decorator; frontend Login/Register pages wired to `AuthContext`
- [ ] **Module 4** — Profile management: view/edit profile, profile picture upload (secure file handling, size/type limits)
- [ ] **Module 5** — Public landing page: nav bar (Home/About/Healthy Foods/Workouts/BMI Calculator/Contact/Login/Register), healthcare-themed content per `SYSTEM.md`
- [ ] **Module 6** — BMI Calculator (stateless endpoint + frontend widget, category display)
- [ ] **Module 7** — Authenticated dashboard: profile summary, BMI, body type, latest meal/workout plan, charts, quick actions
- [ ] **Module 8** — AI dataset preparation: source/curate body-image dataset (Kaggle-first), preprocessing scripts in `ai_model/preprocessing/`
- [ ] **Module 9** — CNN training pipeline (`ai_model/training/`), export versioned model to `ai_model/saved_models/`, record in `ai_model_files` table
- [ ] **Module 10** — Image analysis module: upload → validation → OpenCV preprocessing → CNN inference API → `image_analysis_records`, wired to frontend upload page
- [ ] **Module 11** — Recommendation engine: pure rule-based lookup service triggered after classification, populates `user_recommendations`
- [ ] **Module 12** — Meal plan module: Sri Lankan food data, meal plan detail pages, nutrition breakdown
- [ ] **Module 13** — Workout plan module: workout detail pages, weekly schedule display
- [ ] **Module 14** — Admin panel: CRUD for users, meal/workout plans, foods, body types, BMI categories — no CNN retraining required
- [ ] **Module 15** — Swagger docs pass over every endpoint (`/api/docs`)
- [ ] **Module 16** — Testing pass: backend unit/integration tests per service, frontend component tests, fix gaps found
- [ ] **Module 17** — Deployment (see below)

## Module 17 — Deployment (default plan, adjust if you have a preferred host)

- Containerize backend (`Dockerfile`) and add `docker-compose.yml` for backend + MySQL for local/demo parity.
- Suggested low-cost hosting for an FYP demo: backend on Render or Railway, MySQL on Railway/Clever Cloud (or your university's server if required for submission), frontend on Vercel or Netlify.
- Environment variables set via host dashboard, never committed. `SECRET_KEY`/`JWT_SECRET_KEY` regenerated for production (don't reuse dev values).
- Run migrations against the production DB before first deploy (`flask db upgrade`).
- Enable HTTPS (host default certs are fine), lock CORS to the real frontend origin, disable Flask debug mode.
- Smoke-test `/api/health` and `/api/health/db` against the deployed backend before declaring this module done.
- Write final `documentation/module_reports/module17.md` with live URLs and a one-page "how to redeploy" note.
