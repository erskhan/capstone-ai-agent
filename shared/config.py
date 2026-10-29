"""Application configuration from environment variables."""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", 8000))
    api_workers: int = int(os.getenv("API_WORKERS", 4))

    # Database Configuration
    database_url: str = os.getenv(
        "DATABASE_URL", "mysql+pymysql://root:WP@12345@localhost:3306/loan_approval_dev"
    )

    # Streamlit Configuration
    streamlit_port: int = int(os.getenv("STREAMLIT_SERVER_PORT", 8501))
    streamlit_address: str = os.getenv("STREAMLIT_SERVER_ADDRESS", "localhost")

    # LangSmith Configuration
    langsmith_api_key: str = os.getenv("LANGSMITH_API_KEY", "")
    langsmith_base_url: str = os.getenv(
        "LANGSMITH_BASE_URL", "https://api.smith.langchain.com"
    )
    langsmith_project: str = os.getenv("LANGSMITH_PROJECT", "loan_approval_system")
    langsmith_tracing: bool = (
        os.getenv("LANGSMITH_TRACING", "true").lower() == "true"
    )

    # Security Configuration
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiration_hours: int = int(os.getenv("JWT_EXPIRATION_HOURS", 24))

    # Email Configuration
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", 587))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from_email: str = os.getenv(
        "SMTP_FROM_EMAIL", "noreply@loanapproval.com"
    )

    # Feature Flags
    enable_async_processing: bool = (
        os.getenv("ENABLE_ASYNC_PROCESSING", "true").lower() == "true"
    )
    enable_notifications: bool = (
        os.getenv("ENABLE_NOTIFICATIONS", "false").lower() == "true"
    )
    enable_manual_review_queue: bool = (
        os.getenv("ENABLE_MANUAL_REVIEW_QUEUE", "true").lower() == "true"
    )

    # Performance Configuration
    agent_timeout_seconds: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", 30))
    workflow_timeout_seconds: int = int(os.getenv("WORKFLOW_TIMEOUT_SECONDS", 60))
    api_rate_limit_per_minute: int = int(
        os.getenv("API_RATE_LIMIT_PER_MINUTE", 100)
    )

    class Config:
        """Pydantic config."""

        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
