"""Flask application factory."""

import os

from flask import Flask

from app.config import config_by_name
from app.extensions import bcrypt, cors, db, jwt, migrate
from app.utils.errors import register_error_handlers
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
    cors.init_app(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)

    register_error_handlers(app)

    if not app.testing:
        configure_logging(app)

    from app.routes.health import health_bp

    app.register_blueprint(health_bp)

    from app.seed import register_seed_command

    register_seed_command(app)

    return app
