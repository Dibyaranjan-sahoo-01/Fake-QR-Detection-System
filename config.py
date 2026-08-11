"""
config.py
---------
Central configuration for the Fake QR Code Detection System.
All environment-specific and tunable settings live here so the
rest of the codebase never hardcodes paths, keys, or thresholds.
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration shared by all environments."""

    # --- Flask core ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.environ.get("FLASK_DEBUG", "True") == "True"

    # --- Database ---
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'database', 'database.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- File uploads ---
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "gif", "webp"}
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB max upload size

    # --- Reports ---
    CSV_REPORT_FOLDER = os.path.join(BASE_DIR, "reports", "csv")
    PDF_REPORT_FOLDER = os.path.join(BASE_DIR, "reports", "pdf")

    # --- Risk scoring thresholds ---
    RISK_SAFE_MAX = 25        # score <= 25  -> Safe
    RISK_SUSPICIOUS_MAX = 55  # 26-55        -> Suspicious
    # score > 55               -> Dangerous

    # --- Optional external threat-intel APIs ---
    # Leave blank to disable; the app degrades gracefully to local heuristics.
    GOOGLE_SAFE_BROWSING_API_KEY = os.environ.get("GOOGLE_SAFE_BROWSING_API_KEY", "")
    VIRUSTOTAL_API_KEY = os.environ.get("VIRUSTOTAL_API_KEY", "")

    # --- Admin panel ---
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")  # change in production!


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
