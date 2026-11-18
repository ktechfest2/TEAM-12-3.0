from clarion_api.adapters.llm.base import LanguageModel
from clarion_api.adapters.llm.fake import FakeLanguageModel
from clarion_api.config import Settings


def build_language_model(settings: Settings) -> LanguageModel:
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


__all__ = ["LanguageModel", "build_language_model"]
