import json
from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE_PATH = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ENV_FILE_PATH), extra="ignore")

    DATABASE_URL: str = Field(validation_alias=AliasChoices("DATABASE_URL", "DB_URL"))
    MIGRATION_DATABASE_URL: str | None = Field(
        default=None,
        validation_alias=AliasChoices("MIGRATION_DATABASE_URL", "ALEMBIC_DATABASE_URL"),
    )
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
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001" 
    QDRANT_HOST: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "SmartCorpe"
    CLOUDFLARE_ACCOUNT_ID: str | None = None
    CLOUDFLARE_ACCESS_KEY: str | None = None
    CLOUDFLARE_SECRET_KEY: str | None = None
    CLOUDFLARE_BUCKET_NAME: str | None = None
    CLOUDFLARE_PUBLIC_URL: str | None = None
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"
    LOCAL_STORAGE_ROOT: str = "./app/doc/uploads"
    INGESTION_MAX_LOCAL_CONCURRENCY: int = 2
    INGESTION_SLOT_ACQUIRE_TIMEOUT_SECONDS: int = 5
    INGESTION_RETRY_BASE_SECONDS: int = 15
    INGESTION_RETRY_MAX_SECONDS: int = 300
    INGESTION_DISTRIBUTED_LIMIT_ENABLED: bool = False
    INGESTION_DISTRIBUTED_MAX_CONCURRENCY: int = 4
    INGESTION_DISTRIBUTED_SLOT_TTL_SECONDS: int = 900
    INGESTION_DISTRIBUTED_COUNTER_KEY: str = "smartcope:ingestion:inflight"
    INGESTION_DISTRIBUTED_REDIS_URL: str | None = None
    DOCUMENTS_MAX_OFFSET: int = 10000
    ROLE_MANAGER_ALLOWLIST: str = "admin"
    OPENAI_API_KEY: str | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENAI_API_KEY", "OPENAI_KEY", "OpenAI_Key"),
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def migration_database_url(self) -> str:
        # Use direct Neon endpoint for migrations when provided.
        return self.MIGRATION_DATABASE_URL or self.DATABASE_URL

    @property
    def role_manager_allowlist(self) -> list[str]:
        raw = self.ROLE_MANAGER_ALLOWLIST.strip()

        # Support both CSV (admin,manager) and JSON array (["admin","manager"]).
        candidates: list[str]
        if raw.startswith("[") and raw.endswith("]"):
            try:
                parsed = json.loads(raw)
                candidates = [str(role) for role in parsed] if isinstance(parsed, list) else [raw]
            except json.JSONDecodeError:
                candidates = [raw]
        else:
            candidates = raw.split(",")

        normalized = [
            " ".join(role.strip().lower().split())
            for role in candidates
            if role and str(role).strip()
        ]
        return normalized or ["admin"]


@lru_cache
def get_settings() -> Settings:
    return Settings()