from datetime import UTC, datetime

import pytest

from clarion_api.adapters.llm import build_language_model
from clarion_api.adapters.llm.budget import (
    BudgetedLanguageModel,
    MemoryUsageCounter,
    month_key,
)
from clarion_api.adapters.llm.fake import FakeLanguageModel
from clarion_api.config import AppEnv, Settings
from clarion_api.domain.enums import Language
from clarion_api.domain.errors import LlmBudgetExceededError
from tests.factories import passage

JANUARY = datetime(2027, 1, 15, tzinfo=UTC)
FEBRUARY = datetime(2027, 2, 1, tzinfo=UTC)


def _model(
    counter: MemoryUsageCounter, *, budget_usd: float, clock: datetime = JANUARY
) -> BudgetedLanguageModel:
    # 1,000,000 USD per million tokens: one token costs exactly one USD, so caps are easy to hit.
    return BudgetedLanguageModel(
        FakeLanguageModel(dimensions=8),
        counter,
        monthly_budget_usd=budget_usd,
        usd_per_million_tokens=1_000_000,
        clock=lambda: clock,
    )


async def test_calls_under_the_cap_pass_through_and_are_counted() -> None:
    counter = MemoryUsageCounter()
    model = _model(counter, budget_usd=100)
    [vector] = await model.embed(["hello world"])
    assert len(vector) == 8
    assert await counter.total(month_key(JANUARY)) > 0


async def test_call_past_the_cap_is_refused_with_a_clear_error() -> None:
    counter = MemoryUsageCounter()
    model = _model(counter, budget_usd=2)
    await model.embed(["a long enough sentence to cost more than two tokens"])
    with pytest.raises(LlmBudgetExceededError, match="monthly language model budget"):
        await model.embed(["one more"])


async def test_every_model_operation_is_guarded() -> None:
    counter = MemoryUsageCounter()
    model = _model(counter, budget_usd=1)
    await model.embed(["spend the whole budget with this sentence"])
    with pytest.raises(LlmBudgetExceededError):
        await model.translate("hello", target=Language.YORUBA)
    with pytest.raises(LlmBudgetExceededError):
        await model.judge_claim("a claim", [passage()])


async def test_a_new_month_starts_with_a_fresh_budget() -> None:
    counter = MemoryUsageCounter()
    await _model(counter, budget_usd=1).embed(["spend the whole budget with this sentence"])
    with pytest.raises(LlmBudgetExceededError):
        await _model(counter, budget_usd=1).embed(["blocked"])
    assert await _model(counter, budget_usd=1, clock=FEBRUARY).embed(["fresh month"])


async def test_factory_wraps_the_fake_model_with_a_guard() -> None:
    settings = Settings(app_env=AppEnv.TEST, llm_monthly_budget_usd=0.0, _env_file=None)  # type: ignore[call-arg]
    model = build_language_model(settings)
    assert isinstance(model, BudgetedLanguageModel)
    with pytest.raises(LlmBudgetExceededError):
        await model.embed(["anything"])
