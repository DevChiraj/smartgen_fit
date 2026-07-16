# Module 6 — BMI Calculator

**Status:** Complete
**Branch:** `feature/module-6-bmi-calculator` → `dev`

## What was built

### Backend (`backend/`)
- **`POST /api/v1/bmi/calculate`** — stateless, **no auth required** (matches `SYSTEM.md` §5's "stateless utility" description and the public `/bmi-calculator` nav page). Takes `height_cm`/`weight_kg`, returns the computed BMI and its category.
- **`services/bmi_service.py`**: `calculate_bmi` (standard `weight_kg / height_m²`, `Decimal` arithmetic rounded to 1 decimal place — matching the `bmi_categories.min_bmi`/`max_bmi` column precision from Module 2) and `classify_bmi`.
- **`repositories/bmi_category_repository.py`**: looks up the matching row from the `bmi_categories` table seeded in Module 2 — **not** a re-hardcoded copy of the thresholds, so there's a single source of truth. Ranges are min-inclusive/max-exclusive, and a BMI at or above the highest defined category (currently "Obese", capped at 60 in the seed data) still falls back to that top category instead of returning no match.
- **`schemas/bmi_schema.py`**: `height_cm` restricted to 50–250, `weight_kg` to 2–300 — rejects nonsense input (0, negative, unrealistic) server-side before it ever reaches the calculation.

### Frontend (`frontend/`)
- **`pages/BMICalculator.jsx`** replaces the `ComingSoon` placeholder at `/bmi-calculator` from Module 5. Pre-fills height/weight from the logged-in user's profile (Module 4 data) when available, but works fully for anonymous visitors too. Result is shown as the BMI number plus a colored category badge (info/success/warning/danger mapped to Underweight/Normal/Overweight/Obese).
- **`services/bmiService.js`**: `calculateBmi`.

## How to test locally

**Backend**
```
cd backend
pytest       # 42 passed
flake8 .      # clean
flask run
curl -X POST localhost:5000/api/v1/bmi/calculate -H "Content-Type: application/json" \
  -d '{"height_cm":170,"weight_kg":65}'
```

**Frontend**
```
cd frontend
npm run lint     # 0 errors, 1 pre-existing benign warning
npm run build    # succeeds
npm run dev      # visit /bmi-calculator
```

## Verification performed this session

- 42/42 pytest passing (10 new): correct BMI math, all four categories, the min-inclusive/max-exclusive boundary (exactly 18.5 lands in "Normal weight", not "Underweight"), the open-ended top-category fallback (BMI of 88.9 still classifies as "Obese" rather than null), validation rejects missing/zero/unrealistic input, and confirms the endpoint needs no auth token. flake8 clean.
- **Full real-stack verification, driven by an actual headless browser** (not just curl): started the backend against real MySQL, confirmed `POST /api/v1/bmi/calculate` against the real seeded `bmi_categories` table (including the 88.9-BMI fallback case), then drove the frontend in Playwright — filled the form, submitted, and asserted the displayed BMI value (`22.5`), category text (`Normal weight`), and badge color class (`text-bg-success`) all matched, with zero console errors. Screenshot reviewed directly.
- Cleaned up all dev-server processes afterward and confirmed the ports were actually free (learned from Module 5's stale-process incident).

## Deferred / notes

- Nothing is persisted — by design, per `SYSTEM.md`'s "stateless utility" framing. If a future module wants BMI history tracking, that's a different, explicitly-stateful feature, not this one.
- The category ranges (and their upper bound of 60 for "Obese") are Module 2's seed data, not hardcoded here — if that seed data is edited or extended, this endpoint picks it up automatically with no code change.

## Next

Module 7 — Authenticated dashboard: profile summary, BMI, body type, latest meal/workout plan, charts, quick actions.
