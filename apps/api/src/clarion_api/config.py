"""Typed settings. The only module that reads environment variables.

Names are vendor neutral (LLM_*, SPEECH_*, STORAGE_*, CHANNEL_*). A provider is
chosen by its *_PROVIDER value; code never branches on a vendor name elsewhere.
"""

from enum import StrEnum
from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../../.env"), extra="ignore")

    # runtime
    app_env: AppEnv = AppEnv.DEVELOPMENT
    app_base_url: str = "http://localhost:8000"
    public_web_url: str = "http://localhost:5173"
    log_level: str = "info"
    log_format: Literal["console", "json"] = "console"
    cors_allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    # data, queue
    database_url: str = "postgresql+asyncpg://clarion:clarion@localhost:5432/clarion"
    redis_url: str = "redis://localhost:6379/0"

    # storage
    storage_provider: Literal["local", "s3"] = "local"
    storage_bucket: str = "clarion-media"
    storage_endpoint_url: str | None = None
    storage_region: str | None = None
    storage_access_key_id: SecretStr | None = None
    storage_secret_access_key: SecretStr | None = None
    storage_public_base_url: str | None = None
    storage_local_dir: str = "./var/media"

    # language model
    llm_provider: Literal["fake", "gemini"] = "fake"
    llm_api_key: SecretStr | None = None
    llm_model: str | None = None
    llm_embedding_model: str | None = None
    llm_embedding_dimensions: int = 768
    llm_timeout_seconds: float = 30.0
    llm_monthly_budget_usd: float = 20.0

    # speech
    speech_provider: Literal["fake"] = "fake"
    speech_api_key: SecretStr | None = None
    speech_base_url: str | None = None

    # channels
    channel_telegram_bot_token: SecretStr | None = None
    channel_telegram_chat_id: str | None = None
    channel_sms_provider: str | None = None
    channel_sms_api_key: SecretStr | None = None
    channel_sms_sender_id: str | None = None
    channel_whatsapp_token: SecretStr | None = None
    channel_whatsapp_phone_number_id: str | None = None

    # security
    auth_jwt_secret: SecretStr = SecretStr("change-me-in-every-environment")
    auth_reviewer_invite_code: SecretStr | None = None

    @property
    def is_test(self) -> bool:
        return self.app_env is AppEnv.TEST


@lru_cache
def get_settings() -> Settings:
    return Settings()
