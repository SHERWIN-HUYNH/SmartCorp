from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = Field(validation_alias=AliasChoices("DATABASE_URL", "DB_URL"))
    JWT_ACCESS_SECRET: str = Field(
        validation_alias=AliasChoices("JWT_ACCESS_SECRET", "SECRET", "SECRET_KEY")
    )
    JWT_REFRESH_SECRET: str = Field(
        validation_alias=AliasChoices("JWT_REFRESH_SECRET", "REFRESH_TOKEN_SECRET")
    )
    JWT_ALGORITHM: str = Field(default="HS256", validation_alias=AliasChoices("JWT_ALGORITHM", "ALGORITHM"))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    COOKIE_SECURE: bool = False
    COOKIE_DOMAIN: str | None = None
    CORS_ORIGINS: str = "http://localhost:3000"
    QDRANT_HOST: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "SmartCorp"
    CLOUDFLARE_ACCOUNT_ID: str | None = None
    CLOUDFLARE_ACCESS_KEY: str | None = None
    CLOUDFLARE_SECRET_KEY: str | None = None
    CLOUDFLARE_BUCKET_NAME: str | None = None
    CLOUDFLARE_PUBLIC_URL: str | None = None

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()