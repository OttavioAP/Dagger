import os
from pydantic_settings import BaseSettings
from pydantic import computed_field
from pathlib import Path


class AppSettings(BaseSettings):
    LOG_LEVEL: str = "INFO"
    LLM_API_BASE_URL: str | None = None
    LLM_MODEL_NAME: str | None = None
    EMBEDDING_API_BASE_URL: str | None = None
    EMBEDDING_MODEL_NAME: str | None = None
    LLM_API_KEY: str | None = None
    EMBEDDING_API_KEY: str | None = None
    POSTGRES_DB_NAME: str | None = None
    POSTGRES_DB_USER: str | None = None
    POSTGRES_DB_PASSWORD: str | None = None
    POSTGRES_DB_HOST: str | None = None
    POSTGRES_DB_PORT: int | None = None
    GEMINI_MODEL_NAME: str | None = None
    GEMINI_API_KEY: str | None = None

    class ConfigDict:
        env_prefix = ""
        case_sensitive = True

    @computed_field
    def _database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_DB_USER}:{self.POSTGRES_DB_PASSWORD}@{self.POSTGRES_DB_HOST}:{self.POSTGRES_DB_PORT}/{self.POSTGRES_DB_NAME}"


app_settings = AppSettings()
