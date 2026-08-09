"""Flask application factory."""

import os

from flasgger import Swagger
from flask import Flask

from app.config import config_by_name
from app.docs.swagger_config import SWAGGER_CONFIG, SWAGGER_TEMPLATE
from app.extensions import bcrypt, cors, db, jwt, migrate
from app.utils.errors import register_error_handlers, register_jwt_error_handlers
from app.utils.logger import configure_logging

from app import models  # noqa: F401 - registers models with SQLAlchemy metadata


def create_app(config_name: str | None = None) -> Flask:
    config_name = config_name or os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    register_jwt_error_handlers(jwt)
    cors.init_app(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)
    Swagger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)

    register_error_handlers(app)

    if not app.testing:
        configure_logging(app)

    from app.routes.health import health_bp
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.bmi import bmi_bp
    from app.routes.recommendations import recommendations_bp
    from app.routes.image_analysis import image_analysis_bp
    from app.routes.foods import foods_bp
    from app.routes.exercises import exercises_bp
    from app.routes.admin import admin_bp
    from app.routes.workout_logs import workout_logs_bp
    from app.routes.meal_logs import meal_logs_bp
    from app.routes.notifications import notifications_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(bmi_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(image_analysis_bp)
    app.register_blueprint(foods_bp)
    app.register_blueprint(exercises_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(workout_logs_bp)
    app.register_blueprint(meal_logs_bp)
    app.register_blueprint(notifications_bp)

    from app.seed import register_seed_command
    from app.seed_recommendation_data import register_seed_recommendation_command
    from app.register_model import register_model_command
    from app.promote_admin import register_promote_admin_command

    register_seed_command(app)
    register_seed_recommendation_command(app)
    register_model_command(app)
    register_promote_admin_command(app)

    return app
