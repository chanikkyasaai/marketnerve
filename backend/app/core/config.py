import os
from pathlib import Path
from pydantic_settings import BaseSettings

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_DIR = ROOT_DIR / "config"

class Settings(BaseSettings):
    # AI — Mistral (primary), Gemini/Anthropic/Groq (fallbacks)
    mistral_api_key: str = ""
    gemini_api_key: str = ""
    anthropic_api_key: str = ""
    groq_api_key: str = ""

    # Database
    database_url: str = ""

    # Upstash Redis
    upstash_redis_rest_url: str = ""
    upstash_redis_rest_token: str = ""

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Pipeline
    pipeline_interval_minutes: int = 30
    signal_cache_ttl_seconds: int = 1800
    pattern_cache_ttl_seconds: int = 1800

    # Data path (seed fallback)
    marketnerve_data_path: str = ""

    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def get_cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def get_data_path(self) -> Path:
        if self.marketnerve_data_path:
            return Path(self.marketnerve_data_path)
        return CONFIG_DIR / "marketnerve.seed.json"

    @property
    def has_mistral(self) -> bool:
        return bool(self.mistral_api_key and len(self.mistral_api_key) > 10)

    @property
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key and self.gemini_api_key.startswith("AIza"))

    @property
    def has_anthropic(self) -> bool:
        return bool(self.anthropic_api_key and self.anthropic_api_key.startswith("sk-ant"))

    @property
    def has_groq(self) -> bool:
        return bool(self.groq_api_key and self.groq_api_key.startswith("gsk_"))

    @property
    def has_ai(self) -> bool:
        return self.has_mistral or self.has_gemini or self.has_anthropic or self.has_groq

    @property
    def has_database(self) -> bool:
        return bool(self.database_url)

    @property
    def has_redis(self) -> bool:
        return bool(self.upstash_redis_rest_url and self.upstash_redis_rest_token)

settings = Settings()

def get_data_path() -> Path:
    return settings.get_data_path()
