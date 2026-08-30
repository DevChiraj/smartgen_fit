# Module 15 — Swagger Documentation Pass

**Status:** Complete
**Branch:** `feature/module-15-swagger-docs` → `dev`

## Scope

Document every existing endpoint at `/api/docs` — no new features, no API changes, purely
documentation over the API surface built across Modules 1-14. `flasgger==0.9.7.1` was already sitting
in `backend/requirements.txt` since the Module 1 scaffolding commit, never actually wired up —
confirmed via `git log` before starting, which settled the library choice without needing to compare
Flasgger against Flask-RESTX (SYSTEM.md's stack table had left both options open): Flasgger integrates
with the project's existing vanilla Flask Blueprints via a decorator, with no need to rewrite every
route onto Flask-RESTX's `Resource` classes.

## What was built

### Wiring (`backend/app/docs/swagger_config.py`, `app/__init__.py`)
`Swagger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)` — served at `/api/docs`, raw spec
at `/api/docs/apispec.json`. The template defines the API title/description (including a pointer to
rules 1/2 from `CLAUDE.md`, so anyone reading the docs sees the classify/match boundary explained,
not just endpoint shapes), a `BearerAuth` security scheme for the JWT `Authorization: Bearer <token>`
header, and 9 tags matching the 9 blueprints (Health/Auth/Users/BMI/Image Analysis/Recommendations/
Foods/Exercises/Admin) so Swagger UI groups endpoints sensibly.

### One YAML spec per endpoint (`backend/app/docs/<blueprint>/<endpoint>.yml`)
37 files, one per operation (not per route — `/users/me` has separate `get_me.yml`/`update_me.yml`
for its GET and PUT), each with `tags`, `summary`, `description` (only where genuinely useful -
several note real operational behavior a schema alone wouldn't show, e.g. that `/health/db` returns
503 not 500 when the database is down, or that the CNN in `/image-analysis` is a documented
proof-of-concept), `parameters`, and `responses` covering every status code the controller/service
layer can actually produce (400/401/403/404/409/500/503 as applicable, not just the 200 path).
Referenced from each route with `@swag_from("../docs/<blueprint>/<endpoint>.yml")`.

Shared response shapes (`UserPublic`, `SriLankanFood`, `Exercise`, `AdminUser`, `BMICategory`,
`BodyTypeCategory`, `ImageAnalysisRecord`) are defined once (in whichever file first needs them) and
referenced via `$ref: '#/definitions/...'` everywhere else — Flasgger merges every YAML file's
`definitions` block into one global spec, so this avoids re-describing the same fields in multiple
places and drifting out of sync.

### Coverage regression test (`backend/tests/test_swagger.py`)
`test_every_registered_route_is_documented` walks `app.url_map.iter_rules()`, converts Flask's
`<int:id>` path syntax to Swagger's `{id}` style, and asserts every `(path, method)` pair (excluding
Flasgger's own internal routes and auto-added HEAD/OPTIONS) appears in the generated spec. This is
the actual safety net for the module's goal: a future module that adds a route without a
`@swag_from` decorator now fails a test immediately, rather than silently shipping undocumented.
Also covers that `/api/docs/` (the UI) and `/api/docs/apispec.json` (the raw spec) both return 200,
and that the spec's title matches.

## How to test locally

```
cd backend
pytest                          # 97 passed
flake8 .                        # clean
flask run
# open http://localhost:5000/api/docs/ in a browser
```

## Verification performed this session

- 97/97 backend pytest passing (3 new: docs UI serves, spec JSON is valid, and the full-coverage
  regression check). `flake8`/`black` clean.
- Confirmed via direct spec inspection that all 37 registered operations (9 blueprints, every method
  on every path) are present with zero gaps - listed every documented `(path, methods)` pair and
  cross-checked it against a fresh `grep` of every route decorator in `app/routes/`.
- **Full real-stack Playwright verification**: loaded `/api/docs/` against the real running backend,
  confirmed all 9 tag groups render with the correct endpoint counts and lock icons on JWT-protected
  operations, then ran an actual **"Try it out"** request against the live `POST /bmi/calculate`
  endpoint through the Swagger UI itself (not just the spec) - typed a real request body, hit
  Execute, and confirmed a real 200 response with the correct BMI value and category came back from
  the real backend. Screenshot reviewed showing the full request/response cycle. (One cosmetic,
  non-blocking `Uncaught (in promise) ReferenceError: None is not defined` JS console error surfaced
  during verification - a known quirk of this old, unmaintained Flasgger version's bundled UI
  bundle; it doesn't affect any documented functionality, confirmed by the fully working Try-it-out
  flow above.)

## Deferred / known limitations

- Flasgger 0.9.7.1 (last released 2020) generates Swagger 2.0, not OpenAPI 3 - fine for this
  project's needs (a working interactive reference), but worth noting if a future module wants
  OpenAPI-3-only tooling.
- Request/response schemas are hand-written YAML, not auto-derived from the existing marshmallow
  `Schema` classes - they were written by reading each schema/controller pair directly, so they
  should match, but there's no automated check tying a YAML spec to its marshmallow schema if one
  changes later. The coverage test only guarantees every route *has* docs, not that the docs stay
  in sync with a schema edit.

## Next

Module 16 — Testing pass: backend unit/integration tests per service, frontend component tests, fix
gaps found.
