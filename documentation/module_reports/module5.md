# Module 5 — Public Landing Page

**Status:** Complete
**Branch:** `feature/module-5-landing-page` → `dev`

## What was built

Frontend-only module, no backend changes.

- **`components/Navbar.jsx`**: Bootstrap navbar with all six links from `SYSTEM.md`'s nav spec (Home/About/Healthy Foods/Workouts/BMI Calculator/Contact), auth-aware right side (Login/Register when signed out; username-linking-to-profile + Log out when signed in), and a self-contained mobile toggle using local React state (no Bootstrap JS/Popper dependency needed, since only the CSS bundle is installed).
- **`components/Footer.jsx`**: minimal site footer.
- **`layouts/PublicLayout.jsx`**: now wraps every public page with the Navbar and Footer (`d-flex flex-column min-vh-100` so the footer sticks to the bottom on short pages).
- **`pages/About.jsx`**: healthcare-themed content — the "How it works" 3-step flow (upload → AI classifies body type → rule-based plan lookup) and an explicit "Our AI boundary" section restating the project's hard rule (AI classifies only, never generates advice).
- **`pages/Contact.jsx`**: simple static contact info.
- **`pages/ComingSoon.jsx`**: reusable placeholder, parameterized by title/description, used for the three nav links whose real pages belong to later modules:
  - `/healthy-foods` → Module 12 (meal plan module)
  - `/workouts` → Module 13 (workout plan module)
  - `/bmi-calculator` → Module 6 (**next module** — shortest-lived placeholder)

  This keeps the nav bar fully functional today without pre-building pages that belong to other modules, and without leaving dead 404 links.
- **`pages/LandingPage.jsx`**: rebuilt with real hero/features/AI-boundary content per `SYSTEM.md`. The Module 1 health-check widget (API/DB status badges) was removed from the public-facing page — it was a developer QA tool, not user-facing content, and isn't part of any described feature. `components/HealthStatusCard.jsx` and `services/healthService.js` were deleted since nothing referenced them afterward (backend `/api/health` and `/api/health/db` themselves are untouched and still tested).
- `App.jsx`: added routes for `/about`, `/contact`, `/healthy-foods`, `/workouts`, `/bmi-calculator`.

## How to test locally

```
cd frontend
npm run lint     # 0 errors, 1 pre-existing benign warning (AuthContext.jsx, unchanged since Module 1)
npm run build    # succeeds
npm run dev      # visit /, /about, /contact, /healthy-foods, /workouts, /bmi-calculator, /login, /register
```

## Verification performed this session

- `npm run lint` / `npm run build` both clean.
- **Actually drove the app in a headless browser** (Playwright, installed to a scratch dir — not a project dependency) rather than relying on route-status curls alone. This caught a real bug curl couldn't have: a stale `vite` dev-server process left running on port 5173 from earlier testing was serving 500s on every module (the port cascade had pushed the *current* server to 5176 without me noticing). Killed all stray dev-server processes, restarted clean, and re-ran the check — all 6 pages render their expected content, navbar + footer present on every page, **zero console errors**.
- Confirmed react-router's `NavLink` + Bootstrap's `.nav-link.active` styling correctly highlight the current page in the nav — no extra code needed, verified via screenshot.
- Screenshots reviewed directly (home page and the BMI Calculator placeholder) to confirm the layout actually looks right, not just that it renders without throwing.

## Deferred / notes

- If a future session starts a dev server and doesn't clean it up, subsequent sessions can silently hit a stale/broken instance on the expected port while a working one runs elsewhere — worth remembering to check `netstat`/kill stray processes before trusting a `curl` result against a hardcoded port.
- The three `ComingSoon` placeholders are real, intentional UI (not stubs) — when Module 6/12/13 land, they replace the `ComingSoon` element at the same route rather than needing new nav wiring.

## Next

Module 6 — BMI Calculator: stateless endpoint + frontend widget, category display. Replaces the `/bmi-calculator` placeholder.
