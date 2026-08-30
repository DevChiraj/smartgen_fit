# Module 3 — Authentication

**Status:** Complete
**Branch:** `feature/module-3-auth` → `dev`

## What was built

### Backend (`backend/`)
Full layered slice for auth, matching the architecture from `SYSTEM.md` §2:

- **`app/schemas/auth_schema.py`** (marshmallow, added to `requirements.txt`): `RegisterSchema`, `LoginSchema`, `UserPublicSchema`. Validates email format, username (`^[a-zA-Z0-9_]{3,50}$`), password (min 8 chars), gender (`male`/`female`/`other`). `age` is **not** an input field — it's always computed server-side from `date_of_birth`, never trusted from the client.
- **`app/repositories/user_repository.py`**: `get_by_id`, `get_by_email`, `get_by_username`, `create`.
- **`app/services/auth_service.py`**: `register_user` (enforces the 15-year minimum via `utils/validators.calculate_age`, checks email/username uniqueness, hashes the password with `flask-bcrypt`), `authenticate` (looks up by email *or* username, verifies hash), `generate_tokens` (JWT access + refresh via Flask-JWT-Extended, `role`/`username` embedded as additional claims).
- **`app/controllers/auth_controller.py`** + **`app/routes/auth.py`**: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh` (requires a refresh token), `GET /api/v1/auth/me` (requires an access token) — all under the `/api/v1` prefix per `SYSTEM.md` §5 (health checks stay unversioned at `/api/health`, a deliberate Module 1 choice for infra probes).
- **`app/utils/decorators.py`**: `role_required(*roles)` — the protected-route decorator the roadmap calls for, built on `@jwt_required()` plus a role check, ready for Module 14's admin endpoints.
- **`app/utils/exceptions.py`** + **`app/utils/errors.py`**: domain errors (`DuplicateResourceError` → 409, `InvalidCredentialsError` → 401, `UnderMinimumAgeError` → 400, `ForbiddenError` → 403) all render through the same centralized `{error, message, status}` JSON shape. Flask-JWT-Extended's built-in error callbacks (missing/invalid/expired token) were also hooked up to match that shape, so the frontend only ever has to handle one error format.
- **`app/config.py`**: added `JWT_ACCESS_TOKEN_EXPIRES` (1 hour) / `JWT_REFRESH_TOKEN_EXPIRES` (30 days).

### Frontend (`frontend/`)
- **`services/apiClient.js`**: request interceptor now attaches `Authorization: Bearer <token>` from `localStorage` automatically.
- **`services/authService.js`**: `register`, `login`, `fetchCurrentUser`.
- **`context/AuthContext.jsx`**: now holds `user` (not just `token`); on mount, if a token exists it calls `/me` to hydrate the user and clears storage if the token's stale. `login(authResponse)` stores both tokens and the user object in one call.
- **`pages/Login.jsx`**, **`pages/Register.jsx`**: real forms wired to `AuthContext`. Register includes a client-side age pre-check (immediate feedback) — the server is still the enforcing authority.
- **`utils/age.js`**, **`utils/formatApiError.js`**, **`utils/storageKeys.js`**: small shared helpers (age math, turning the backend's error shape — string or marshmallow's field→messages dict — into readable text, centralized localStorage keys).
- **`pages/LandingPage.jsx`**: now auth-aware — shows Login/Register links when signed out, a welcome message + logout button when signed in (this is a minimal QA affordance, not the real navbar — that's Module 5).
- `App.jsx`: added `/login` and `/register` routes.

## How to test locally

**Backend**
```
cd backend
pytest                # 23 passed
flake8 .               # clean
flask run
curl -X POST localhost:5000/api/v1/auth/register -H "Content-Type: application/json" \
  -d '{"full_name":"Jane Doe","date_of_birth":"2000-01-01","gender":"female","email":"jane@example.com","username":"jane_doe","password":"supersecret"}'
```

**Frontend**
```
cd frontend
npm run lint      # 0 errors, 1 benign fast-refresh warning (pre-existing, same as Module 1)
npm run build     # succeeds
npm run dev       # visit /register, /login
```

## Verification performed this session

- 23/23 pytest passing (13 new auth tests + 3 new decorator tests), `flake8` clean.
- **Full round-trip against your real local MySQL** (not the throwaway SQLite used in Module 2's verification): register → login (both by username and by email) → `/me` → `/refresh` → duplicate email/username rejected (409) → wrong password rejected (401) → missing token rejected (401), all over HTTP with `curl`. The smoke-test user was deleted afterward.
- Confirmed CORS headers are correct on the auth endpoints (not just `/health`) when called with the frontend's origin.
- Frontend `/login` and `/register` routes resolve and build cleanly; `role_required` was verified with dedicated tests (dynamically-registered test routes — blocks wrong role with 403, allows matching role, rejects missing token with 401) since there's no real admin endpoint yet to exercise it against.

## Deferred / notes

- No refresh-token rotation or revocation list — a stolen refresh token is valid until it expires (30 days). Acceptable for an FYP scope; flag it if you want rotation added later.
- `role_required` has no live production endpoint yet (only test-only routes exercise it) — it'll get its first real use in Module 14 (admin panel).
- Registration only accepts `male`/`female`/`other` for gender, but Module 2's seeded meal/workout plans only cover `male`/`female` combinations. A user who registers as `other` will hit a gap once Module 11 (recommendation engine) does its lookup — worth deciding the fallback then.
- `JWT_SECRET_KEY`'s dev default is short enough that PyJWT emits an `InsecureKeyLengthWarning` in tests — harmless for dev, but make sure your real `.env` `JWT_SECRET_KEY` is long/random, especially before Module 17 (deployment) reuses these values.
- Carried forward a small fix you'd already made locally: `config.py`'s MySQL fallback default now matches your working local setup (`root` with no password, db name `smartgen_fit_db`).

## Next

Module 4 — Profile management: view/edit profile (`GET/PUT /users/me`), profile picture upload with secure file handling (size/type limits).
