from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # FastAPI settings
    PROJECT_NAME: str = "Humana API"
    API_STR: str = "/api"
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1  # 1 day
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"
    API_KEY: str = "your-api-key-here"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "places_db"
    SQLALCHEMY_DATABASE_URI: str | None = None
    MAIL_TRAP_API_KEY: str = ""
    MAIL_TRAP_INBOX_ID: int = 0
    RESET_PASSWORD_URL: str = "http://localhost:3000/reset-password"

    POSTGRES_MONO_HOST: str = "localhost"
    POSTGRES_MONO_SERVER: str = "0.0.0.0"
    POSTGRES_MONO_PORT: int = 5432
    POSTGRES_MONO_USER: str = "user"
    POSTGRES_MONO_PASSWORD: str = "postgres"
    POSTGRES_MONO_DB: str = "oncall_pay_db"
    SQLALCHEMY_MONO_DATABASE_URI: str | None = None

    # Logging configuration
    ENVIRONMENT: str = "development"  # development, staging, production
    LOG_LEVEL: str = "INFO"
    SQLALCHEMY_ECHO: bool = False  # Set to True only for SQL debugging
    TIMEZONE: str = "America/Sao_Paulo"

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = ""
    S3_ENDPOINT_URL: str | None = None

    # Google AI
    GOOGLE_API_KEY: str = ""

    # Extra configs
    API_PORT: int = 8000
    POSTGRES_SERVER: str = "localhost"
    COMPOSE_PROJECT_NAME: str | None = None

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not self.LOG_LEVEL or not self.LOG_LEVEL.strip():
            self.LOG_LEVEL = "INFO"

    @property
    def get_database_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"


settings = Settings()
