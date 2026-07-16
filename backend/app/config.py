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
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB request body cap

    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER", os.path.join(PROJECT_ROOT, "uploads", "profile_pictures")
    )
    PROFILE_PICTURE_MAX_BYTES = 2 * 1024 * 1024  # 2 MB per file
    PROFILE_PICTURE_ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


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
