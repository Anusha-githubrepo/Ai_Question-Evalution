from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Question Evaluator"
    environment: str = "development"
    database_url: str = "sqlite:///./app.db"
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    llm_provider: str = "groq"
    allow_local_fallback: bool = Field(default=False)
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    enable_sentence_transformers: bool = Field(default=True)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def normalized_provider(self) -> str:
        return self.llm_provider.strip().lower()


@lru_cache
def get_settings() -> Settings:
    return Settings()
