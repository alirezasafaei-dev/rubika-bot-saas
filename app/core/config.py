# app/core/config.py
from typing import Annotated

from pydantic import BeforeValidator, Field, PostgresDsn, RedisDsn
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

    # App
    app_name: str = "Rubika Bot SaaS"
    app_version: str = "0.1.0"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: Annotated[PostgresDsn, BeforeValidator(parse_postgres_dsn)] = Field(
        default=PostgresDsn("postgresql+psycopg://user:pass@localhost:5432/rubika_bot")
    )

    # Redis
    redis_url: Annotated[RedisDsn, BeforeValidator(parse_redis_dsn)] = Field(
        default=RedisDsn("redis://localhost:6379/0")
    )

    # Auth
    jwt_secret_key: str = Field(default="CHANGE_ME_IN_PRODUCTION")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Security
    argon2_time_cost: int = 2
    argon2_memory_cost: int = 65536
    argon2_parallelism: int = 1


settings = Settings()
