"""Production configuration for Flask API."""

import os


class Config:
    """Base configuration."""

    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

    # API settings
    API_HOST = os.environ.get("API_HOST", "127.0.0.1")
    API_PORT = int(os.environ.get("API_PORT", 5000))
    API_DEBUG = os.environ.get("API_DEBUG", "False").lower() == "true"

    # Agent pipeline settings
    MAX_STEPS = int(os.environ.get("MAX_STEPS", 5))
    PER_STEP_RETRIES = int(os.environ.get("PER_STEP_RETRIES", 3))
    REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", 60))

    # CORS settings
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")

    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    # Rate limiting (requests per minute)
    RATE_LIMIT = int(os.environ.get("RATE_LIMIT", 30))

    # Database settings (if needed)
    DATABASE_URL = os.environ.get("DATABASE_URL")

    # Model settings
    USE_HUGGINGFACE = os.environ.get("USE_HUGGINGFACE", "False").lower() == "true"
    HF_MODEL_NAME = os.environ.get("HF_MODEL_NAME", "microsoft/DialoGPT-medium")

    # Security
    ENABLE_AUTH = os.environ.get("ENABLE_AUTH", "False").lower() == "true"
    API_KEY = os.environ.get("API_KEY")


class DevelopmentConfig(Config):
    """Development configuration."""

    API_DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration."""

    API_DEBUG = False
    SECRET_KEY = os.environ.get("SECRET_KEY") or "production-secret-key-required"
    ENABLE_AUTH = True
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "https://yourdomain.com").split(",")


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    API_DEBUG = True
    RATE_LIMIT = 1000  # Higher rate limit for testing


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Get configuration based on environment."""
    env = os.environ.get("FLASK_ENV", "development")
    return config.get(env, config["default"])
