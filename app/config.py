from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./akup.db"
    echo_sql: bool = False

    model_config = {"env_prefix": "AKUP_", "env_file": ".env"}


settings = Settings()
