"""Flasgger configuration: served at /api/docs, one YAML spec per endpoint
under app/docs/<blueprint>/<endpoint>.yml (see individual route files'
@swag_from decorators). Kept out of app/__init__.py to keep the app
factory focused on wiring, not documentation content.
"""

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/api/docs/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs/",
}

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "SmartGen Fit API",
        "description": (
            "AI-Powered Personalized Nutrition and Fitness Recommendation System. "
            "Body images are classified by a CNN (Thin/Normal/Overweight only - see "
            "rule 1 in CLAUDE.md); meal/workout recommendations are a KNN similarity "
            "match against real datasets, never generated at request time (rule 2)."
        ),
        "version": "1.0.0",
    },
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": 'JWT access token, e.g. "Bearer <token>". Obtained from '
            "POST /auth/login or /auth/register.",
        }
    },
    "tags": [
        {"name": "Health", "description": "Liveness/readiness checks"},
        {"name": "Auth", "description": "Registration, login, JWT refresh"},
        {"name": "Users", "description": "Profile view/edit, profile picture upload"},
        {"name": "BMI", "description": "Stateless BMI calculation"},
        {
            "name": "Image Analysis",
            "description": "Body photo upload -> CNN classification -> KNN recommendation match",
        },
        {"name": "Recommendations", "description": "The user's latest matched meal + workout plan"},
        {"name": "Foods", "description": "Public Sri Lankan food/nutrition reference data"},
        {"name": "Exercises", "description": "Public exercise reference library"},
        {"name": "Admin", "description": "Admin-only management (role=admin required)"},
        {
            "name": "Workout Logs",
            "description": "The user's real logged history of completed workouts",
        },
    ],
}
