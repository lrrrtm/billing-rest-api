from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/billing"
    jwt_secret: str = "super-secret-jwt-key-with-32-chars-min"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    webhook_secret: str = "gfdmhghif38yrf9ew0jkf32"
    log_level: str = "INFO"

    @property
    def sync_database_url(self) -> str:
        if self.database_url.startswith("postgresql+asyncpg://"):
            return self.database_url.replace(
                "postgresql+asyncpg://",
                "postgresql+psycopg://",
                1,
            )
        return self.database_url


class SettingsProxy:
    def __getattr__(self, name: str):
        return getattr(Settings(), name)


settings = SettingsProxy()
