# Module 16 — Testing Pass

**Status:** Complete
**Branch:** `feature/module-16-testing-pass` → `dev`

## Approach: data-driven, not "chase 100%"

Before writing anything, I audited actual state: backend had 97 passing tests but zero coverage
tooling installed, so "97 tests" was a raw count, not a coverage measurement. The frontend had
**zero** test infrastructure — every one of the previous 14 feature modules was verified via
`npm run build`/`npm run lint`/real headless-browser Playwright walkthroughs instead, deliberately
deferred to this module each time.

Rather than write tests speculatively, I installed `pytest-cov`, ran a real coverage report, and used
the actual missing-line output to decide what to add — closing genuine gaps (a data-loading function
with zero direct tests, an off-by-one-prone age calculation branch, a CLI command layer nothing had
ever invoked) while deliberately skipping low-value lines chasing coverage for its own sake (model
`__repr__` methods, the non-testing-mode logging setup, JWT error branches for features this app
doesn't implement like token revocation). Coverage went from **94% → 99%** (97 → 137 tests), not
100% — the remaining 1% is verified-not-worth-it, not overlooked.

## Backend: gap-filling (`backend/tests/`)

Real gaps found and closed, by file:
- **`meal_recommendation_repository.py` / `workout_recommendation_repository.py`** (33% → 100%) —
  `bulk_upsert()` and `count()`, the actual data-loading logic behind `flask seed-recommendations`,
  had **zero** direct tests since Module 11 (only verified by hand against real MySQL that session).
  New `test_meal_recommendation_repository.py` / `test_workout_recommendation_repository.py` cover
  create, update-by-`Person_ID`, and idempotency directly.
- **`seed_recommendation_data.py`** (45% → 100%) — the xlsx-parsing functions, same situation. New
  `test_seed_recommendation_data.py` builds small synthetic xlsx files (mirroring the pattern already
  used for the food/exercise loaders) and asserts real column parsing, including the
  `Equipment` NaN→`None` conversion for bodyweight exercises.
- **`app/utils/validators.py`** (86% → 100%) — `calculate_age()`'s "birthday hasn't happened yet this
  year" branch was never exercised. This guards rule 4 (minimum age 15) directly; an off-by-one here
  could misjudge a real registrant's age by a year.
- **`app/utils/errors.py`** (87% → 95%) — added tests for the expired-JWT-token handler (a real,
  reachable state given `JWT_ACCESS_TOKEN_EXPIRES`) and the generic unhandled-exception handler
  (confirms internal error details never leak to the client). Left the `needs_fresh_token`/
  `revoked_token` handlers untested — this app doesn't implement token freshness requirements or a
  revocation blocklist, so those branches are genuinely unreachable, not just untested.
- **`recommendation_service.py`** (91% → 100%) — direct tests for both "matched a `Person_ID`
  the candidate tables don't actually have" 500 branches (real referential-integrity guards, hard to
  reach via full HTTP integration tests without deliberately corrupting data) and the BMI fallback
  branch (uses the matched candidate's own BMI when the user's profile has no height/weight yet).
- **`bmi_category_service.py` / `body_type_service.py`** (91%/92% → 100%) — `NotFoundError` branches
  reachable via `/admin/bmi-categories/:id` and `/admin/body-types/:id` with an unknown id; added as
  new cases in `test_admin.py` alongside a couple of missing success-path tests (`GET` single user,
  `GET` BMI category list) that the Module 14 session hadn't covered.
- **`app/utils/file_handler.py`** (94% → 100%) — new `test_file_handler.py` covers the no-file,
  empty-filename, and no-extension validation branches directly with a `werkzeug.FileStorage`, rather
  than only through a real multipart upload.
- **CLI command layer** (`register_model.py` 75%→100%, `promote_admin.py` 88%→100%) — new
  `test_cli_commands.py` invokes all four registered `flask` commands (`seed`,
  `seed-recommendations`, `register-model`, `promote-admin`) through `app.test_cli_runner()`. Every
  underlying business function already had direct tests; the `@app.cli.command` wrapper itself
  (argument parsing, the echoed confirmation) had never been exercised by anything but a human typing
  `flask ...` by hand.

`pytest-cov` added to `requirements.txt`; coverage config in `pyproject.toml` (`source = ["app"]`,
`omit = ["app/utils/logger.py"]` — file-handler config only active outside test mode, not meaningfully
testable without contorting the setup).

## Frontend: test framework from scratch

**Tooling decision:** Vitest + React Testing Library + `@testing-library/user-event` + `jsdom`.
Neither `CLAUDE.md` nor `SYSTEM.md` named a preference, so I picked the standard modern pairing for a
Vite project (Vitest reuses the existing `vite.config.js` and Vite's transform pipeline directly,
rather than needing a separate Jest/Babel config alongside Vite). Added a `test` block to
`vite.config.js` (`environment: 'jsdom'`, a `src/test/setup.js` importing `@testing-library/jest-dom`),
and `npm run test` / `npm run test:watch` scripts.

**Scope:** rather than write shallow tests for all 17 pages, I prioritized real logic and a
representative sample of UI patterns:
- **Utils** (3 files, 20 tests) — `formatApiError`, `age` (`calculateAge`, mirrors the backend's own
  age edge cases), `weeklySchedule` (the Module 13 day-spread algorithm, previously only verified
  manually in a Playwright session — now encoded as `it.each` assertions for every `daysPerWeek`
  value 1-7).
- **Services** (9 files, 35 tests) — every one of the 9 API-wrapper modules, verifying the correct
  HTTP method/URL/payload shape against a mocked `apiClient`, plus a dedicated `apiClient.test.js` for
  the JWT-attaching request interceptor itself (the one piece of real logic in that file).
- **`AuthContext`** (7 tests) — `useAuth` throwing outside a provider, cold start with/without a
  stored token, a stale/rejected token clearing storage and logging out, `login`/`logout`, and
  `refreshUser`. Surfaced one real (pre-existing, not introduced by this module) behavior worth
  knowing: `login()` changes `token` state, which re-triggers the same effect that fetches the
  current user on mount — so a real `/auth/me` call follows every login even though the login
  response already carried the user object. Not fixed here (out of scope for a testing pass, and
  low-impact - one redundant GET), but now documented via the test itself rather than silent.
- **Route guards** (`ProtectedRoute`, `AdminRoute`, 7 tests) — loading/unauthenticated/wrong-role/
  authorized states for both, mocking `useAuth`.
- **Representative pages** (5 files, 20 tests): `BMICalculator` (profile pre-fill, submit, error),
  `Login` (success + failure paths), `Register` (the real client-side under-15 rejection using
  `calculateAge`, successful registration with the `phone_number`-omitted-when-empty payload
  transform, server-side error display), `Dashboard` (all four conditional states: no user, missing
  height/weight, BMI shown, recommendation present vs. absent), `HealthyFoods` (debounced search,
  category filter, detail modal, error state) — deliberately chosen to cover five distinct UI
  patterns (form+validation, form+redirect, form+business-rule, multi-state conditional rendering,
  list+filter+modal) rather than exhaustively testing all 17 pages for marginal additional value.

`frontend-ci.yml` gained a `Test` step (`npm run test`) between lint and build, and the job was
renamed `lint-test-and-build` to match. Backend CI already ran `pytest` unconditionally, so
`pytest-cov`'s presence needed no CI change there.

## How to test locally

**Backend**
```
cd backend
pytest --cov=app --cov-report=term-missing   # 137 passed, 99% coverage
flake8 .                                      # clean
```

**Frontend**
```
cd frontend
npm run test     # 89 passed across 20 files
npm run lint     # 0 errors, 1 pre-existing benign warning
npm run build    # succeeds
```

## Verification performed this session

- Backend: 137/137 passing, 99% line coverage (up from 94%/97 tests), `flake8`/`black` clean. Every
  new test targets a line the coverage report proved was actually missing, not a speculative
  duplicate of existing integration coverage.
- Frontend: 89/89 passing across 20 new test files, `eslint` clean (fixed a handful of unused-import
  lint errors introduced while writing the tests), `npm run build` still succeeds.
- Confirmed both CI workflows pick up the new test steps by construction (`frontend-ci.yml`'s job
  now runs lint → test → build in order; `backend-ci.yml`'s existing `pytest` step now exercises 40
  more tests without any workflow change needed).

## Deferred / known limitations

- Frontend coverage is intentionally not exhaustive - 12 of 17 pages (mostly static/informational:
  `About`, `Contact`, `LandingPage`, the five `admin/Admin*.jsx` CRUD pages, `Profile`,
  `ImageAnalysis`, `MealPlanDetail`, `Workouts`) have no dedicated component test yet. The five tested
  pages were chosen to cover distinct patterns/logic, not because the untested ones are less
  important - a future pass could extend coverage to the admin CRUD pages in particular, which have
  real logic (self-delete disabling, form validation) similar to what's already tested elsewhere.
- No frontend code-coverage tooling (e.g. `@vitest/coverage-v8`) was installed - the backend's
  `pytest-cov` report was what drove this module's gap-finding; the frontend test set was scoped by
  manual code-reading instead, since there was no prior baseline to measure against.
- The `AuthContext` redundant-refetch-after-login behavior noted above is left as-is (documented via
  the test, not changed) since fixing it wasn't identified as a real problem, just a minor
  inefficiency, and this module's job is exposing/covering real behavior, not tuning UX/performance.

## Next

Module 17 — Deployment: containerize the backend, add `docker-compose.yml` for local/demo parity,
deploy per the plan already sketched in `CLAUDE.md`, smoke-test the live health endpoints, and write
a final report with live URLs and a redeploy guide.
