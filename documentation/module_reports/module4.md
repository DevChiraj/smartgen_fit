# Module 4 — Profile Management

**Status:** Complete
**Branch:** `feature/module-4-profile` → `dev`

## What was built

### Backend (`backend/`)
- **`GET /api/v1/users/me`** — returns the authenticated user's profile (now includes `phone_number`, `height_cm`, `weight_kg`, `profile_picture_url` alongside the fields Module 3 already exposed).
- **`PUT /api/v1/users/me`** — partial update of `full_name`, `phone_number`, `height_cm`, `weight_kg`. `UserUpdateSchema` uses `unknown = EXCLUDE`, so extra/unknown fields (e.g. a client accidentally sending `role`) are silently dropped rather than erroring the whole request or ever being settable.
- **`POST /api/v1/users/me/profile-picture`** — multipart upload, fully guarded in `app/utils/file_handler.py`:
  - extension allow-list (`png`, `jpg`, `jpeg`, `webp`),
  - size cap (2 MB per file, separate from the global 5 MB request-body cap already set in Module 1),
  - **real content verification** — the file is opened with Pillow (`Image.open(...).verify()`), so a `.txt` renamed to `.png` is rejected, not just extension-sniffed,
  - stored under a UUID filename (no client-supplied names, no path-traversal surface), and the previous picture is deleted on replace so uploads don't accumulate orphaned files.
- **`GET /api/v1/users/uploads/profile-pictures/<filename>`** — serves the saved images via `send_from_directory` (public, like a normal avatar URL; not access-controlled to the owner since avatars are meant to be viewable, same as most apps).
- **Refactor**: `UserPublicSchema` moved from `schemas/auth_schema.py` to its own `schemas/user_schema.py` (auth still imports it from there) — it's a user concern, not an auth concern, and Module 4 needed to extend it.
- `config.py` gained `UPLOAD_FOLDER` (resolved from `__file__`, so it's correct regardless of the process's working directory — the repo-root `uploads/profile_pictures/`, matching `SYSTEM.md` §3), `PROFILE_PICTURE_MAX_BYTES`, `PROFILE_PICTURE_ALLOWED_EXTENSIONS`.
- `Pillow` added to `requirements.txt`.

### Frontend (`frontend/`)
- **`services/userService.js`**: `getMe`, `updateMe`, `uploadProfilePicture` (builds `FormData`).
- **`components/ProtectedRoute.jsx`**: redirects to `/login` if not authenticated; waits for `AuthContext`'s hydration (`isLoading`) before deciding, so a logged-in user isn't flash-redirected on refresh.
- **`pages/Profile.jsx`**: shows the read-only identity fields (username/email/gender/age), an edit form for the editable ones, and a photo uploader with a live preview of the current picture.
- **`AuthContext`**: added `refreshUser()` so the profile page (and anywhere else) can re-pull `/me` after an edit and keep the header/landing-page welcome text in sync without a full reload.
- **`apiClient.js`**: exports `API_ORIGIN` (backend origin derived from `VITE_API_BASE_URL`) since the frontend and backend run on different origins in dev — profile picture `<img>` tags need the full backend URL, not a bare relative path.
- Landing page now links to `/profile` when signed in.

## How to test locally

**Backend**
```
cd backend
pytest                # 32 passed
flake8 .               # clean
flask run
curl -X PUT localhost:5000/api/v1/users/me -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" -d '{"full_name":"New Name"}'
curl -X POST localhost:5000/api/v1/users/me/profile-picture \
  -H "Authorization: Bearer <token>" -F "profile_picture=@avatar.png"
```

**Frontend**
```
cd frontend
npm run lint     # 0 errors, 1 pre-existing benign warning (AuthContext.jsx, same as Modules 1/3)
npm run build    # succeeds
npm run dev      # log in, visit /profile
```

## Verification performed this session

- 32/32 pytest passing (9 new profile/upload tests), flake8 clean. Upload tests cover: success, non-image content rejected (400), disallowed extension rejected (400), oversized file rejected (400), and replacing a picture deletes the old file (asserted both via the old URL 404ing and only one file remaining on disk).
- Test uploads are isolated to a per-test `tmp_path` (via a `conftest.py` fixture override), confirmed the real tracked `uploads/` folder has zero test leakage.
- **Full manual round-trip against your real local MySQL and real filesystem**: register → GET profile → PUT profile (persisted correctly) → upload a real Pillow-generated PNG → fetched it back over HTTP (`200`, `image/png`) → confirmed a non-image and a disallowed extension are both rejected (`400`). Smoke-test user and its uploaded file were both cleaned up afterward.
- Frontend `npm run build` succeeds; `/profile` is wired behind `ProtectedRoute`.

## Deferred / notes

- Email and username are intentionally **not** editable in this module — changing either touches identity/uniqueness logic similar to registration (and, in a real product, usually needs re-verification). Flag it if you want that added; scoped out to keep this module focused.
- `date_of_birth`/`gender` are also not editable here for the same reason — changing DOB would require re-running the age/minimum-age check.
- Profile picture URLs are unauthenticated/publicly fetchable by anyone with the link (UUID filenames make them unguessable, but there's no ownership check on the `GET` route) — standard for avatar images, flagging in case you want it locked down later.
- No image resizing/thumbnailing — whatever the user uploads (up to 2 MB) is served as-is. Worth revisiting if the dashboard (Module 7) ends up needing consistent thumbnail sizes.

## Next

Module 5 — Public landing page: nav bar (Home/About/Healthy Foods/Workouts/BMI Calculator/Contact/Login/Register), healthcare-themed content per `SYSTEM.md`.
