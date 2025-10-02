"""
Configuration management for Text-to-SQL Assistant
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class"""

    # Application
    APP_NAME: str = os.getenv("APP_NAME", "Text-to-SQL Assistant")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/demo.sqlite")
    DATABASE_TYPE: str = os.getenv("DATABASE_TYPE", "sqlite")

    # Model Configuration
    MODEL_NAME: str = os.getenv("MODEL_NAME", "google/flan-t5-base")
    MODEL_CACHE_DIR: str = os.getenv("MODEL_CACHE_DIR", "./models")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "128"))
    NUM_BEAMS: int = int(os.getenv("NUM_BEAMS", "4"))
    MAX_INPUT_LENGTH: int = int(os.getenv("MAX_INPUT_LENGTH", "400"))

    # Streamlit Configuration
    STREAMLIT_SERVER_PORT: int = int(
        os.getenv("PORT", os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    )
    STREAMLIT_SERVER_ADDRESS: str = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")
    STREAMLIT_THEME_BASE: str = os.getenv("STREAMLIT_THEME_BASE", "light")

    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_WORKERS: int = int(os.getenv("API_WORKERS", "1"))

    # Safety Configuration
    DEFAULT_QUERY_LIMIT: int = int(os.getenv("DEFAULT_QUERY_LIMIT", "200"))
    MAX_QUERY_LIMIT: int = int(os.getenv("MAX_QUERY_LIMIT", "10000"))
    ENABLE_SAFETY_CHECKS: bool = (
        os.getenv("ENABLE_SAFETY_CHECKS", "True").lower() == "true"
    )

    # Performance Configuration
    ENABLE_MODEL_CACHING: bool = (
        os.getenv("ENABLE_MODEL_CACHING", "True").lower() == "true"
    )
    MODEL_LOAD_TIMEOUT: int = int(os.getenv("MODEL_LOAD_TIMEOUT", "60"))
    QUERY_TIMEOUT: int = int(os.getenv("QUERY_TIMEOUT", "30"))

    # Evaluation Configuration
    EVALUATION_RESULTS_DIR: str = os.getenv("EVALUATION_RESULTS_DIR", "results")
    EVALUATION_REPORTS_DIR: str = os.getenv("EVALUATION_REPORTS_DIR", "results/reports")
    EVALUATION_BENCHMARKS_DIR: str = os.getenv(
        "EVALUATION_BENCHMARKS_DIR", "results/benchmarks"
    )
    EVALUATION_TIMEOUT: int = int(os.getenv("EVALUATION_TIMEOUT", "300"))
    MAX_EVALUATION_QUESTIONS: int = int(os.getenv("MAX_EVALUATION_QUESTIONS", "100"))

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        required_settings = ["DATABASE_URL", "MODEL_NAME"]

        for setting in required_settings:
            if not getattr(cls, setting):
                raise ValueError(f"Required setting {setting} is not configured")

        return True

    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL with fallback"""
        if cls.DATABASE_URL.startswith("sqlite:///"):
            # Ensure the directory exists for SQLite
            db_path = cls.DATABASE_URL.replace("sqlite:///", "")
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)

        return cls.DATABASE_URL


# Global config instance
config = Config()

# Validate configuration on import
try:
    config.validate()
except ValueError as e:
    print(f"Configuration error: {e}")
    print("Please check your environment variables or .env file")
