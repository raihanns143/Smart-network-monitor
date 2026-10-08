"""
app/config.py
=============
Centralised configuration for the Flask application.
Reads from environment variables (loaded via python-dotenv from .env).
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration — shared across all environments."""

    # ------------------------------------------------------------------
    # Flask core
    # ------------------------------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    DEBUG = False
    TESTING = False

    # ------------------------------------------------------------------
    # SQLAlchemy / MySQL
    # ------------------------------------------------------------------
    DB_HOST     = os.environ.get("DB_HOST",     "localhost")
    DB_PORT     = os.environ.get("DB_PORT",     "3306")
    DB_USER     = os.environ.get("DB_USER",     "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_NAME     = os.environ.get("DB_NAME",     "smart_network_monitor")

    # Use DATABASE_URL if set (e.g. a hosted MySQL/Postgres URL).
    # Fall back to SQLite for zero-config environments like Vercel.
    _mysql_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    _sqlite_url = "sqlite:////tmp/smart_network_monitor.db"
    
    _has_mysql_config = any([
        os.environ.get("DB_HOST") and os.environ.get("DB_HOST") != "localhost",
        os.environ.get("DATABASE_URL"),
    ])
    
    if os.environ.get("VERCEL"):
        # On Vercel, always use SQLite unless a remote DATABASE_URL is explicitly provided
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or _sqlite_url
    else:
        SQLALCHEMY_DATABASE_URI = (
            os.environ.get("DATABASE_URL")
            or (_mysql_url if _has_mysql_config else _sqlite_url)
        )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
    }

    # ------------------------------------------------------------------
    # Flask-Login
    # ------------------------------------------------------------------
    SESSION_COOKIE_HTTPONLY  = True
    SESSION_COOKIE_SAMESITE  = "Lax"
    REMEMBER_COOKIE_DURATION = 86400  # 1 day in seconds

    # ------------------------------------------------------------------
    # Application-specific
    # ------------------------------------------------------------------
    SCAN_INTERVAL   = int(os.environ.get("SCAN_INTERVAL",   "30"))
    NETWORK_RANGE   = os.environ.get("NETWORK_RANGE",   "192.168.1.0/24")
    ADMIN_USERNAME  = os.environ.get("ADMIN_USERNAME",  "admin")
    ADMIN_PASSWORD  = os.environ.get("ADMIN_PASSWORD",  "Admin@1234")
    ADMIN_EMAIL     = os.environ.get("ADMIN_EMAIL",     "admin@networkmonitor.local")


class DevelopmentConfig(Config):
    """Development environment — verbose debugging."""
    DEBUG = True
    SQLALCHEMY_ECHO = False   # set True to log all SQL queries


class ProductionConfig(Config):
    """Production environment — security hardened."""
    SESSION_COOKIE_SECURE = True


# Map string name → class
config_map = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "default":     DevelopmentConfig,
}
