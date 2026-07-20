# Module 12 — Meal Plan Module (Sri Lankan Food Data, Detail Pages, Nutrition Breakdown)

**Status:** Complete
**Branch:** `feature/module-12-meal-plans` → `dev`

## Scope decision: what "meal plan detail pages" means post-Module-11

Before writing code, I audited what already existed: `sri_lankan_foods` and `meal_plans`/`workout_plans`
(Module 2 template tables) had DB models and seed data but **zero API layer** (no repository,
service, controller, or route) and zero frontend pages — both were fully stubbed. `SYSTEM.md` had
speculatively documented `GET /meal-plans/:id`/`/workout-plans/:id` back when recommendations were
still the original composite-key lookup.

Since Module 11, `meal_plans`/`workout_plans` are dead data — `image_analysis_service.analyze()`
never populates a row through that path anymore (confirmed: `user_recommendations.meal_plan_id`/
`workout_plan_id` stay null on every new row, only `matched_person_id` gets set). Building a detail
page or API around data no live user flow ever reaches would just be dead surface area, and runs
against this project's consistent preference (established across Modules 10-11) for the real, live
pipeline over legacy scaffolding. So this module does **not** build `/meal-plans/:id` or
`/workout-plans/:id` — `SYSTEM.md` §4/§5 now document this explicitly rather than silently dropping
it.

What Module 12 builds instead, both fully live:
1. **Sri Lankan food data + nutrition breakdown** — a real public food database (`sri_lankan_foods`),
   independent of the recommendation pipeline, browsable via search/category filter.
2. **Meal plan detail page** — a dedicated `/meal-plan` page for the user's *actual* live matched
   plan (Module 11's `meal_recommendation_records`/`workout_recommendation_records`), reusing the
   existing `/recommendations/latest` endpoint rather than adding a duplicate one.

I deliberately did **not** attempt to link the two — e.g. fuzzy-matching "Red Rice + Fish" (a free-text
meal description from the Module 11 dataset) against specific `sri_lankan_foods` rows to compute a
per-meal macro breakdown. The two datasets come from different sources with no reliable text
linkage, and fabricating one would produce plausible-looking but false nutrition numbers — against
this project's consistent anti-fabrication discipline (see Module 8/9's dataset-integrity write-ups).
The meal plan page instead cross-links to the Healthy Foods page for ingredient lookups.

## What was built

### Real dataset (Kaggle, per CLAUDE.md rule 6)
Searched Kaggle for "Sri Lankan food nutrition" and found
`nipunaudara/nutritional-facts-for-most-common-sri-lankan-foods` (CC0-1.0, public domain) — 119 real
foods (rice/bread/curries/fruit/biscuits/dairy/etc.) with Food/Quantity/Calories/Carbohydrate/
Protein/Fat columns. Coverage was good enough that rule 6's manual-data fallback wasn't needed.
Committed to `datasets/sri_lankan_foods/SrilankanCommonFoods.xlsx` (22KB, no license/privacy
concern unlike the body-image dataset, so unlike that dataset this one *is* tracked in git).

### Database (`backend/app/models/sri_lankan_food.py`, migration `75dffec41e61`)
Added `serving_size` (nullable) to `sri_lankan_foods` — the source data separates food name from
serving size ("White Rice", "80g") where the original 12-row placeholder had baked serving info into
the name string ("Red rice (boiled, 1 cup)"); a real column is more honest than continuing that
convention. Applied against real local MySQL, no drift.

### Data loading (`backend/app/seed_food_data.py`)
`load_food_records()` parses the xlsx (strips units: `"110 kcal"` → `110`, `"24g"` → `24.0`) and
assigns `category` via an **explicit 119-entry per-food mapping**, not keyword heuristics — a
keyword rule would misfire on real entries like "Chocolate Marie biscuit" (matches both a "Chocolate"
sweets rule and a "biscuit" snacks rule). The source dataset has no fiber/vitamin/mineral/category
columns; those are left `null` for every Kaggle-sourced row rather than invented. `seed.py`'s
`_seed_foods()` now calls this loader and explicitly deletes any row with `serving_size IS NULL`
first (identifies the old manual placeholder rows) so re-running `flask seed` on a pre-Module-12
database converges to just the real 119-row dataset instead of keeping both — verified: seeded a
database with the old 12-row placeholder present, ran `flask seed`, confirmed exactly 119 rows
remain and none of the placeholder names survived.

### Backend API (`backend/app/routes/foods.py`, public — no auth, matches Healthy Foods being a
public nav page since Module 5)
- `GET /api/v1/foods?category=&q=` — list with optional case-insensitive category filter and
  substring name search.
- `GET /api/v1/foods/categories` — distinct categories for a filter dropdown.
- `GET /api/v1/foods/:id` — full detail (404 via a new `NotFoundError` in `utils/exceptions.py`,
  the first 404 case in the app - previously nothing needed one).
- New `food_repository.py`/`food_service.py`/`food_controller.py`/`food_schema.py`, registered as
  `foods_bp` in `app/__init__.py`.

### Frontend
- **`HealthyFoods.jsx`** (`/healthy-foods`, replaces the Module 5 `ComingSoon` stub) — debounced
  search + category dropdown, a sortable table of all matching foods, click a row for a modal with
  the full nutrition breakdown (calories/protein/carbs/fat, plus fiber/vitamins/minerals when
  present).
- **`MealPlanDetail.jsx`** (`/meal-plan`, new authenticated tab in `AuthenticatedLayout`) — the
  user's full live matched meal + workout plan (same data Dashboard's card summarizes), framed with
  an explicit "matched via KNN, not generated" note and a link to Healthy Foods.
- Dashboard's personalized-plan card gained a "View full plan" link to `/meal-plan`.
- `foodService.js` — `getFoods()`, `getFoodCategories()`, `getFoodById()`.

## How to test locally

**Backend**
```
cd backend
pytest              # 67 passed
flake8 .            # clean
flask db upgrade    # applies the serving_size migration
flask seed          # loads the real 119-row food dataset (idempotent)
flask run
curl "localhost:5000/api/v1/foods?category=Fruit"
curl "localhost:5000/api/v1/foods/categories"
```

**Frontend**
```
cd frontend
npm run lint     # 0 errors, 1 pre-existing benign warning
npm run build    # succeeds
npm run dev      # visit /healthy-foods (no login needed), or log in and visit /meal-plan
```

## Verification performed this session

- 67/67 backend pytest passing (10 new: food list/search/category-filter/detail/404 cases, seed
  count + idempotency using the real loaded count, and a dedicated test confirming a pre-Module-12
  placeholder row gets replaced on re-seed). `flake8`/`black` clean.
- Seeded the real dataset against real local MySQL twice in a row (idempotency: 119 rows both times,
  no duplicates), and separately verified the placeholder-replacement path by seeding a database that
  still had the old 12-row data present.
- **Full real-stack Playwright walkthrough**: loaded `/healthy-foods` unauthenticated and confirmed
  all 119 real foods render; filtered by category (Fruit → 12 rows) and by search ("rice" → 4 rows,
  matching a direct `curl` check); opened a food's detail modal and confirmed its nutrition fields;
  registered a user, set profile height/weight, uploaded a photo, then visited `/meal-plan` before
  and after analysis (correct empty-state CTA, then the full matched plan) and confirmed the
  Dashboard's "View full plan" link navigates there correctly. Screenshots reviewed for the food
  table, the filtered table, the detail modal, and both meal-plan-page states.

## Deferred / known limitations

- No per-meal-item nutrition breakdown (linking "Oats + Papaya" to specific `sri_lankan_foods` rows)
  — deliberately not attempted; see the scope-decision section above.
- `meal_plans`/`workout_plans` template tables and their seed data remain in the schema, unused,
  same as noted in `module11.md` — still not deleted, in case a future module's scope needs them.
- `sri_lankan_foods` has no admin-facing edit UI yet — Module 14 (admin panel) is the natural home
  for that, per `CLAUDE.md`'s existing roadmap entry.
- The Kaggle dataset has no food images; `image_url` stays null for all 119 rows.

## Next

Module 13 — Workout plan module: workout detail pages, weekly schedule display.
