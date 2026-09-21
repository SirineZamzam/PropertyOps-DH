from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "PropertyOps API"

    database_url: str = ""
    test_database_url: str

    frontend_origin: str = "http://localhost:5173"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_currency: str = "usd"
    frontend_url: str = "http://localhost:5173"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"
    ai_max_records_per_type: int = 30
    ai_requests_per_hour: int = 5
    ai_lookback_days: int = 365
    ai_timeout_seconds: int = 30

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()