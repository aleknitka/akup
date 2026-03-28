from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./akup.db"
    echo_sql: bool = False
    secret_key: str = "change-me-in-production"
    auth_mode: str = "local"  # "local" or "oidc"
    oidc_issuer: str = ""
    oidc_audience: str = ""
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    model_config = {"env_prefix": "AKUP_", "env_file": ".env"}


settings = Settings()
