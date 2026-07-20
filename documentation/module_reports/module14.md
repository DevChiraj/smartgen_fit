# Module 14 — Admin Panel

**Status:** Complete
**Branch:** `feature/module-14-admin-panel` → `dev`

## Scope decision: what "CRUD for meal/workout plans" means now

Same audit-before-building approach as Modules 12/13. Research confirmed `role_required(*roles)`
(`backend/app/utils/decorators.py`) and the JWT `role` claim (`auth_service.generate_tokens`)
already existed from an earlier module but were never wired into any production route — reused
as-is. Nothing else admin-related existed: no bootstrap mechanism for the first admin account, no
`AdminLayout`/`AdminRoute` on the frontend, no write operations on any repository.

`CLAUDE.md`'s roadmap line for this module still said "CRUD for users, meal/workout plans, foods,
body types, BMI categories" — predating Module 11. Consistent with Module 12/13's already-documented
decision (`SYSTEM.md` §4/§5 have said this since Module 12), `meal_plans`/`workout_plans` (the
Module 2 template tables) get no admin UI here either: nothing in the live pipeline has populated a
row in either table since Module 11's KNN match replaced the old lookup, so building management
screens for permanently-empty data would be pure dead surface area. The admin panel instead manages
what's actually live: `sri_lankan_foods` (Module 12) and `exercises` (Module 13), plus `users`,
`body_type_categories`, and `bmi_categories`.

**Also deliberately out of scope:** the Module 11 KNN candidate pool (`meal_recommendation_records`/
`workout_recommendation_records`, 2,000 rows each). These are bulk reference data loaded from Kaggle
xlsx files via `flask seed-recommendations`, not the kind of thing an admin hand-edits row by row in
a UI — refreshing the whole dataset (re-running the seed command) is the right operation, not CRUD.

## What was built

### Admin bootstrap (`backend/app/promote_admin.py`)
`flask promote-admin <email>` promotes an already-registered user to `admin`. Deliberately a CLI
command, not an HTTP endpoint — the very first admin (and any admin added outside the panel) needs
direct server/DB access to create, so there is no self-service escalation path a regular user could
ever reach. Verified against the real database: registered a normal user via the real API, then
promoted them via the CLI, confirmed the role change took effect on next login (JWT claims are set
at login time from the DB row, so an already-issued token doesn't retroactively gain admin rights).

### Role guard wiring (`backend/app/routes/admin.py`)
Every route uses the pre-existing `@role_required("admin")` decorator (previously built and tested
but unused). New blueprint at `/api/v1/admin`, registered in `app/__init__.py`.

### Safety guards against admin lockout (`backend/app/services/admin_user_service.py`)
Three real operational risks were guarded against rather than left to "an admin should just be
careful":
- An admin cannot delete their own account through the panel (a mistaken click would need direct DB
  access to undo).
- An admin cannot demote the last remaining admin to `user`.
- An admin cannot delete the last remaining admin.
All three are enforced service-side (checked via `user_repository.count_by_role("admin")`), not just
in the UI, and covered by dedicated tests, including one that exercises the last-admin guard
independently of the self-delete guard by calling the service directly.

### Admin CRUD surface
- **Users** (`GET/PUT/DELETE /admin/users[/:id]`) — list, update (`full_name`, `phone_number`,
  `height_cm`, `weight_kg`, `role`), delete. Reuses the existing `User` model; no new fields.
- **Foods** (`POST/PUT/DELETE /admin/foods[/:id]`) — full CRUD; list/detail stay on the existing
  public `/foods` endpoints from Module 12 rather than duplicating reads under `/admin`.
- **Exercises** (`POST/PUT/DELETE /admin/exercises[/:id]`) — same pattern, reusing Module 13's
  public `/exercises` reads.
- **Body types** (`GET/PUT /admin/body-types[/:id]`) — **description only**. `name` isn't editable:
  `image_analysis_service` looks up the predicted body type by exact name
  (`body_type_repository.get_by_name`) against the CNN's hardcoded `CLASS_NAMES` (Thin/Normal/
  Overweight) — renaming a row would silently break classification for that body type. No create/
  delete either, since the set is architecturally fixed to exactly those three.
- **BMI categories** (`GET/POST/PUT/DELETE /admin/bmi-categories[/:id]`) — full CRUD, with a guard
  against deleting the last remaining category (the BMI calculator needs at least one range to
  classify into).
- New `admin_schema.py` holds every admin-only request/response schema in one place (write schemas
  separate from the public read schemas, since admin payloads have different required/optional
  shapes and expose fields like `role`/`email` the public endpoints don't).

### Frontend
- **`AdminRoute.jsx`** — like `ProtectedRoute` but also checks `user.role === 'admin'`, redirecting
  non-admins to `/dashboard` (they're authenticated, just not authorized, so `/login` would be
  wrong).
- **`AdminLayout.jsx`** — tab nav mirroring `AuthenticatedLayout`'s pattern: Users / Foods /
  Exercises / Body Types / BMI Categories.
- Five pages under `frontend/src/pages/admin/`: table + create/edit modal + delete (with
  `window.confirm`) for Foods/Exercises/BMI Categories; a role-dropdown + delete table for Users
  (self-delete disabled in the UI, matching the backend guard); a simpler description-only editor
  for Body Types.
- `AuthenticatedLayout` gained a conditionally-rendered "Admin" tab, shown only when
  `user.role === 'admin'`.
- `adminService.js` covers every admin endpoint; the read-heavy pages reuse `foodService.js`/
  `exerciseService.js` from Modules 12/13 rather than re-fetching through `/admin`.

## How to test locally

**Backend**
```
cd backend
pytest                              # 94 passed
flake8 .                            # clean
flask run
flask promote-admin you@example.com # after registering normally via the UI/API
```

**Frontend**
```
cd frontend
npm run lint     # 0 errors, 1 pre-existing benign warning
npm run build    # succeeds
npm run dev      # log in as the promoted admin, an "Admin" tab appears
```

## Verification performed this session

- 94/94 backend pytest passing (21 new: access control for every admin route, full CRUD round-trips
  for foods/exercises/BMI categories, body-type description-only editing, all three admin-lockout
  guards, and the `promote-admin` CLI both for a real registered user and an unknown email).
  `flake8`/`black` clean.
- **Full real-stack Playwright walkthrough**: registered a normal user via the real API, promoted
  them to admin via the real CLI against real MySQL, then drove the actual UI — confirmed a regular
  user never sees the Admin tab and is redirected away from `/admin/users`; logged in as the admin,
  confirmed the Admin tab appears and the self-delete button is disabled on their own row; ran a full
  create → edit → delete cycle on a real food and a real exercise through the actual modal forms;
  confirmed the Body Types and BMI Categories pages load real data. Screenshots reviewed for the
  users table (showing the disabled self-delete button) and the body-types editor.
- **Caught and fixed a real environment issue while verifying, not a code bug**: several zombie
  `vite` dev-server processes from earlier module verification sessions were still bound to ports
  5173-5177, and a `pkill -f vite` had silently failed to stop the original one — Playwright kept
  hitting the stale server on 5173 and testing an old, unedited version of the admin forms, which
  looked exactly like a real bug (missing `name` attributes) until traced back to the wrong process
  serving requests. Fixed by force-killing every listener on those ports via `taskkill` before
  starting one clean instance; not a defect in the application code.

## Deferred / known limitations

- No admin UI for `meal_plans`/`workout_plans` (legacy, dead) or the Module 11 KNN candidate pool
  (bulk reference data) — see the scope-decision section above.
- User CRUD doesn't include changing a user's email/username (kept minimal - password resets and
  identity changes carry more security weight than this module's scope; deferring rather than
  building it without more thought).
- No audit log of admin actions (who changed what, when) — worth considering if this were a real
  production deployment with multiple admins.

## Next

Module 15 — Swagger docs pass over every endpoint (`/api/docs`).
