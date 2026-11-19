from clarion_api.adapters.llm.base import LanguageModel
from clarion_api.adapters.llm.budget import (
    BudgetedLanguageModel,
    MemoryUsageCounter,
    RedisUsageCounter,
    UsageCounter,
)
from clarion_api.adapters.llm.fake import FakeLanguageModel
from clarion_api.config import Settings


def build_language_model(settings: Settings, counter: UsageCounter | None = None) -> LanguageModel:
    """Build the configured model and always wrap it in the monthly budget guard."""
    if counter is None:
        offline = settings.llm_provider == "fake" or settings.is_test
        counter = MemoryUsageCounter() if offline else RedisUsageCounter(settings.redis_url)
    return BudgetedLanguageModel(
        _build_provider(settings),
        counter,
        monthly_budget_usd=settings.llm_monthly_budget_usd,
        usd_per_million_tokens=settings.llm_usd_per_million_tokens,
    )


def _build_provider(settings: Settings) -> LanguageModel:
    if settings.llm_provider == "fake" or settings.is_test:
        return FakeLanguageModel(dimensions=settings.llm_embedding_dimensions)
    if settings.llm_provider == "gemini":
        from clarion_api.adapters.llm.gemini import GeminiLanguageModel  # noqa: PLC0415

        if not (settings.llm_api_key and settings.llm_model and settings.llm_embedding_model):
            msg = "LLM_API_KEY, LLM_MODEL and LLM_EMBEDDING_MODEL are required for gemini"
            raise RuntimeError(msg)
        return GeminiLanguageModel(
            api_key=settings.llm_api_key.get_secret_value(),
            model=settings.llm_model,
            embedding_model=settings.llm_embedding_model,
            dimensions=settings.llm_embedding_dimensions,
        )
    msg = f"unknown LLM_PROVIDER: {settings.llm_provider}"
    raise RuntimeError(msg)


__all__ = ["BudgetedLanguageModel", "LanguageModel", "UsageCounter", "build_language_model"]
