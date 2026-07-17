# Module 7 — Authenticated Dashboard

**Status:** Complete
**Branch:** `feature/module-7-dashboard` → `dev`

## A sequencing note up front

The roadmap builds the dashboard (Module 7) before the AI pipeline (Modules 8-10) and the
recommendation engine (Module 11). That means **no user can have a body type or a meal/workout
recommendation yet** — `image_analysis_records` and `user_recommendations` are real tables with
zero rows for everyone, by construction, until those later modules run. The dashboard is built
to be fully honest about that: it shows a real empty state ("You haven't been analyzed yet...")
rather than faking data, and nothing about its API contract needs to change when Module 11
starts actually writing rows.

## What was built

### Backend (`backend/`)
- **`GET /api/v1/recommendations/latest`** — the read endpoint `SYSTEM.md` §4 explicitly ties to
  "drives the Latest Meal/Workout Plan dashboard widgets." This is deliberately scoped as
  **read-only**: it queries whatever's already in `user_recommendations` (nothing today, real
  data once Module 11 lands) and returns `null` when there's nothing yet. It does **not** contain
  any classification or rule-based lookup logic — that's Module 11's `RecommendationService`,
  which creates these rows; this endpoint only reads them, keeping the AI/recommendation boundary
  intact.
- **`repositories/recommendation_repository.py`**: `get_latest_for_user`, ordered by
  `created_at DESC, recommendation_id DESC`. The `recommendation_id` tiebreaker isn't
  decorative — a first draft that sorted by `created_at` alone was already caught failing its
  own test in this session, because two rows created in the same test (and plausibly the same
  request in production, e.g. a retry) can land in the same timestamp tick, making "latest"
  ambiguous. Fixed before merge.
- **`schemas/recommendation_schema.py`**: a deliberately minimal summary shape (plan code +
  calories, not the full breakfast/lunch/dinner/warm-up/cardio text) — full plan detail is
  Module 12/13's job (`GET /meal-plans/:id`, `/workout-plans/:id`).

### Frontend (`frontend/`)
- **`layouts/AuthenticatedLayout.jsx`**: introduces the `AuthenticatedLayout` named in
  `SYSTEM.md` §3 — a small Dashboard/My Profile tab bar wrapping the two protected pages, nested
  inside the existing `PublicLayout` (which still owns the global Navbar/Footer, since the navbar
  already adapts to auth state — no duplication).
- **`pages/Dashboard.jsx`** at `/dashboard`, wrapped in `ProtectedRoute` + `AuthenticatedLayout`:
  - **Profile summary** — name, username, age, gender, avatar (reuses Module 4 data already on
    `AuthContext.user`, no extra fetch).
  - **BMI widget** — reuses the Module 6 `POST /bmi/calculate` endpoint directly against the
    user's saved height/weight (no new backend BMI logic needed). Shows a real progress-bar
    gauge positioned by `(bmi - category.min) / (category.max - category.min)`, using only
    numbers the API actually returned — not a fabricated 4-category background, since the public
    BMI endpoint only returns the one matched category's range. If the profile has no
    height/weight yet, it prompts the user to add them rather than guessing.
  - **Body type & latest plan** — calls the new `/recommendations/latest`; today this always
    renders the honest empty state described above for every real user.
  - **Quick actions** — "Edit profile" and "Recalculate BMI" are real, working links.
    "Analyze body photo" and "Meal & workout plans" are shown as disabled buttons labeled
    "(coming soon)" rather than omitted or linked to nothing — same honesty principle as the
    Module 5 `ComingSoon` pages, applied at the tile level instead of a whole route.
- Navbar's authenticated button and the landing page's authenticated CTA now point at
  `/dashboard` instead of `/profile` (dashboard is the natural "home base" after login; Profile
  is reached from its own tab).

## How to test locally

**Backend**
```
cd backend
pytest       # 46 passed
flake8 .      # clean
flask run
curl -H "Authorization: Bearer <token>" localhost:5000/api/v1/recommendations/latest
```

**Frontend**
```
cd frontend
npm run lint     # 0 errors, 1 pre-existing benign warning
npm run build    # succeeds
npm run dev      # log in, visit /dashboard
```

## Verification performed this session

- 46/46 pytest passing (4 new). The recommendation tests don't just check the empty state —
  one builds the **entire real FK chain** (body type, BMI category, age group, meal plan,
  workout plan, image analysis record, recommendation) to prove the nested dump actually works
  correctly end to end, and another proves "latest" is resolved correctly across multiple rows
  (the test that caught the ordering bug above). flake8 clean.
- **Full real-stack browser verification**: registered a fresh user through the real UI against
  real MySQL, loaded `/dashboard` and confirmed the BMI empty-state prompt and the honest
  "haven't been analyzed yet" message both render correctly for a brand-new account; then filled
  in height/weight on the real Profile page, reloaded the dashboard, and confirmed the BMI
  widget showed the correct computed value (`22.5`), correct category (`Normal weight`), and a
  correctly-filled gauge bar — all against the live backend, zero console errors. Screenshot
  reviewed directly. Smoke-test user cleaned up afterward; all dev-server processes confirmed
  stopped.

## Deferred / notes

- The BMI gauge only shows the current matched category's internal range, not a full
  Underweight→Obese background scale — there's no public endpoint listing all `bmi_categories`
  today (only the future admin CRUD one in Module 14). Worth revisiting if a fuller visual is
  wanted later.
- No historical charting (weight-over-time, BMI trend) — there's no table in the schema for that
  kind of time-series data, and adding one wasn't asked for. Flag it if you want it.
- "Quick actions" only link to what's real today; the two disabled tiles will become real links
  once Modules 10 (image analysis) and 12/13 (meal/workout plans) exist.

## Next

Module 8 — AI dataset preparation: source/curate a body-image dataset (Kaggle-first),
preprocessing scripts in `ai_model/preprocessing/`.
