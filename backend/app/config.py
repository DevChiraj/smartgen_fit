"""Environment-based Flask configuration classes."""

import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))


class Config:
    """Base configuration shared by all environments."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:@localhost:3306/smartgen_fit_db",
    )
    # MySQL closes idle connections (wait_timeout) before SQLAlchemy's pool expires them;
    # without pre_ping, the first request after an idle period fails instead of reconnecting.
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB request body cap

    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER", os.path.join(PROJECT_ROOT, "uploads", "profile_pictures")
    )
    PROFILE_PICTURE_MAX_BYTES = 2 * 1024 * 1024  # 2 MB per file
    PROFILE_PICTURE_ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    BODY_IMAGE_UPLOAD_FOLDER = os.environ.get(
        "BODY_IMAGE_UPLOAD_FOLDER", os.path.join(PROJECT_ROOT, "uploads", "body_images")
    )
    BODY_IMAGE_MAX_BYTES = 4 * 1024 * 1024  # 4 MB per file
    BODY_IMAGE_ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

_DEV_DEFAULT_SECRETS = {
    "SECRET_KEY": "dev-secret-key-change-me",
    "JWT_SECRET_KEY": "dev-jwt-secret-change-me",
}

if os.environ.get("FLASK_ENV") == "production":
    for _env_var, _dev_default in _DEV_DEFAULT_SECRETS.items():
        if os.environ.get(_env_var, _dev_default) == _dev_default:
            raise RuntimeError(
                f"{_env_var} is not set (or still equals its development default). "
                "Refusing to start with FLASK_ENV=production using an insecure secret."
            )
