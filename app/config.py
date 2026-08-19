from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str = Field(alias="BOT_TOKEN")
    api_id: int = Field(alias="API_ID")
    api_hash: str = Field(alias="API_HASH")
    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL")
    ai_api_key: str | None = Field(default=None, alias="AI_API_KEY")
    ai_base_url: str | None = Field(default=None, alias="AI_BASE_URL")
    ai_model: str | None = Field(default=None, alias="AI_MODEL")
    metadata_api_key: str | None = Field(default=None, alias="METADATA_API_KEY")
    metadata_base_url: str | None = Field(default=None, alias="METADATA_BASE_URL")
    admin_ids: str = Field(default="", alias="ADMIN_IDS")
    timezone: str = Field(default="Asia/Kolkata", alias="TIMEZONE")
    media_root: str = Field(default="/data/media", alias="MEDIA_ROOT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    max_upload_retries: int = Field(default=5, alias="MAX_UPLOAD_RETRIES")
    upload_concurrency: int = Field(default=2, alias="UPLOAD_CONCURRENCY")
    processing_concurrency: int = Field(default=1, alias="PROCESSING_CONCURRENCY")
    status_edit_interval: int = Field(default=3, alias="STATUS_EDIT_INTERVAL")
    default_retry_seconds: int = Field(default=30, alias="DEFAULT_RETRY_SECONDS")

    @property
    def admin_id_set(self) -> set[int]:
        return {int(x.strip()) for x in self.admin_ids.split(",") if x.strip()}

@lru_cache
def get_settings() -> Settings:
    return Settings()
