# Module 1 — Project Scaffolding

**Status:** Complete
**Branch:** `feature/module-1-scaffolding` → `dev`

## What was built

### Backend (`backend/`)
- Flask **app factory** (`app/__init__.py`) reading env-based config (`app/config.py`: Development/Testing/Production classes).
- Extensions initialized in one place (`app/extensions.py`): SQLAlchemy, Bcrypt, JWTManager, CORS (scoped to `CORS_ORIGINS`, currently the Vite dev origin).
- Full layered folder skeleton per `SYSTEM.md` §3: `routes/`, `controllers/`, `services/`, `repositories/`, `models/`, `schemas/`, `utils/`, `docs/`.
- First vertical slice through every layer — health checks:
  - `GET /api/health` → static API-alive response.
  - `GET /api/health/db` → runs `SELECT 1` against the configured database, returns `200` if reachable, `503` with an error detail if not.
  - Wired route → controller → service, matching the architecture in `SYSTEM.md` §2.
- Centralized JSON error handlers (`utils/errors.py`) — every error responds `{error, message, status}`.
- Rotating file logger (`utils/logger.py`), off during tests.
- `requirements.txt`, `.env.example`, `setup.cfg` (flake8), `pyproject.toml` (black + pytest config).
- `backend/tests/test_health.py` — exercises both health endpoints against an in-memory SQLite testing config (no live MySQL needed for CI).

### Frontend (`frontend/`)
- Vite + React scaffold, cleaned of template boilerplate.
- Swapped the default `oxlint` for **ESLint 9 + Prettier** (flat config) to match `SYSTEM.md` §7 conventions; `react/prop-types` enforced, all components validated with `prop-types`.
- Full folder skeleton per `SYSTEM.md` §3: `components/`, `pages/` (+ `pages/Admin/`), `layouts/`, `services/`, `context/`, `hooks/`, `utils/`, `styles/`.
- `services/apiClient.js` (axios instance, `VITE_API_BASE_URL`) + `services/healthService.js`.
- `context/AuthContext.jsx` — token/session state stub (localStorage-backed), ready for Module 3 to wire real login/logout calls into.
- `layouts/PublicLayout.jsx`, `components/HealthStatusCard.jsx`, `pages/LandingPage.jsx` — a minimal landing page that calls both backend health endpoints on mount and renders live status. This is the module's end-to-end proof, not a preview of the real Module 5 landing page.
- Bootstrap 5 wired via `styles/global.css`; React Router installed with a single `/` route (routing config ready for Module 3+ to extend).
- `.env.example` for `VITE_API_BASE_URL`.

### Repo-wide
- `ai_model/{notebooks,training,inference,preprocessing,saved_models}/`, `datasets/{body_images,sri_lankan_foods}/`, `uploads/`, `backend/migrations/` created (empty, `.gitkeep`-tracked) so the full `SYSTEM.md` §3 tree exists from the start.
- Root `.gitignore` extended for backend logs, frontend `node_modules`/`dist`, AI model binaries, and uploaded files (folder tracked, contents ignored).

## How to test locally

**Backend**
```
cd backend
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
pytest                          # 2 passed
flake8 .                        # clean
flask --app run.py run          # or: python run.py
curl localhost:5000/api/health
curl localhost:5000/api/health/db
```

**Frontend**
```
cd frontend
npm install
npm run lint                    # 0 errors, 1 benign fast-refresh warning on AuthContext.jsx
npm run build                   # production build succeeds
npm run dev                     # http://localhost:5173 — landing page shows live API/DB status badges
```

Both were run and verified during this session: pytest (2 passed), flake8 (clean), `npm run build` (succeeds), and both dev servers running together with the frontend successfully calling the backend (confirmed via `curl` with CORS headers and by inspecting the health badges' data flow).

## Deferred / notes

- `GET /api/health/db` correctly returns `503` right now — there's no local MySQL server running yet. This is expected, not a bug; it proves the failure path works. Set up MySQL and populate `backend/.env` from `.env.example` to see it return `200`.
- No database models exist yet — Alembic (`Flask-Migrate`) is in `requirements.txt` but `flask db init` hasn't been run; that's Module 2 (`SYSTEM.md` §4 schema).
- No auth logic yet — `AuthContext` only manages local token state; Module 3 adds the real `/auth/*` calls.
- Only `pages/LandingPage.jsx` exists; the rest of `pages/` (Login, Register, Dashboard, BMICalculator, etc.) are intentionally not stubbed out — they'll be built in their respective modules rather than left as empty placeholders.
- An unrelated `postcss.config.mjs` was found in the user's `Documents/` folder (a parent directory, outside this repo) referencing `@tailwindcss/postcss`; Vite's PostCSS resolution was walking up and picking it up, breaking `npm run build`. Fixed by adding an explicit `frontend/postcss.config.js`, which takes precedence — no changes made outside the repo.

## Next

Module 2 — Database schema: SQLAlchemy models for every table in `SYSTEM.md` §4, Alembic migrations, seed script with realistic sample data.
