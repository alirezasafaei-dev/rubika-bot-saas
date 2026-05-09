from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="Rubika Bot SaaS")
    version: str = Field(default="0.1.0")
    api_v1_str: str = Field(default="/api/v1")
    debug: bool = Field(default=False)
    environment: str = Field(default="development")

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/rubika_bot_saas"
    )
    sync_database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/rubika_bot_saas"
    )

    redis_url: str = Field(default="redis://localhost:6379/0")

    jwt_secret_key: str = Field(default="CHANGE_ME_IN_PRODUCTION")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)
    jwt_refresh_token_expire_days: int = Field(default=7)

    @property
    def PROJECT_NAME(self) -> str:
        return self.app_name

    @property
    def VERSION(self) -> str:
        return self.version

    @property
    def API_V1_STR(self) -> str:
        return self.api_v1_str

    @property
    def DEBUG(self) -> bool:
        return self.debug


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
