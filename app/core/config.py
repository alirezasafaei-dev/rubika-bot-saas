# app/core/config.py
from __future__ import annotations

from typing import Annotated

from pydantic import BeforeValidator, Field, PostgresDsn, RedisDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_postgres_dsn(v: str | PostgresDsn) -> PostgresDsn:
    """Parse PostgreSQL DSN from string."""
    if isinstance(v, str):
        return PostgresDsn(v)
    return v


def parse_redis_dsn(v: str | RedisDsn) -> RedisDsn:
    """Parse Redis DSN from string."""
    if isinstance(v, str):
        return RedisDsn(v)
    return v


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Rubika Bot SaaS"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    database_url: Annotated[PostgresDsn, BeforeValidator(parse_postgres_dsn)] = Field(
        default=PostgresDsn("postgresql+asyncpg://user:pass@localhost:5432/rubika_bot")
    )
    redis_url: Annotated[RedisDsn, BeforeValidator(parse_redis_dsn)] = Field(
        default=RedisDsn("redis://localhost:6379/0")
    )

    jwt_secret_key: str = Field(default="CHANGE_ME_IN_PRODUCTION", min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, ge=1, le=1440)
    refresh_token_expire_days: int = Field(default=7, ge=1, le=365)

    argon2_time_cost: int = Field(default=2, ge=1)
    argon2_memory_cost: int = Field(default=65536, ge=8192)
    argon2_parallelism: int = Field(default=1, ge=1)
    argon2_hash_len: int = Field(default=32, ge=16)
    argon2_salt_len: int = Field(default=16, ge=8)

    @model_validator(mode="after")
    def validate_security(self) -> "Settings":
        insecure_values = {
            "CHANGE_ME_IN_PRODUCTION",
            "changeme",
            "secret",
            "default-secret",
            "test-secret",
            "",
        }

        if self.environment.lower() in {"production", "staging"}:
            if self.jwt_secret_key.strip() in insecure_values:
                raise ValueError(
                    "jwt_secret_key is insecure. Set a strong secret in environment variables."
                )

        return self

    # --- Aliases for backward compatibility ---
    @property
    def PROJECT_NAME(self) -> str:
        return self.app_name

    @property
    def VERSION(self) -> str:
        return self.app_version

    @property
    def API_V1_STR(self) -> str:
        return self.api_v1_prefix

    @property
    def DEBUG(self) -> bool:
        return self.debug

    @property
    def SECRET_KEY(self) -> str:
        return self.jwt_secret_key

    @property
    def ALGORITHM(self) -> str:
        return self.jwt_algorithm


settings = Settings()
