"""Monthly spend cap for any language model.

The wrapper estimates cost from text length (about four characters per token),
counts it per calendar month, and refuses new calls once the cap is reached.
Counting lives behind `UsageCounter` so tests need no Redis.
"""

from collections.abc import Callable, Sequence
from datetime import datetime
from typing import Protocol

from redis.asyncio import Redis

from clarion_api.adapters.llm.base import LanguageModel
from clarion_api.domain.enums import Language
from clarion_api.domain.errors import LlmBudgetExceededError
from clarion_api.domain.models import SourcePassage, VerdictResult, utc_now

CHARS_PER_TOKEN = 4
MICRO_USD = 1_000_000
KEY_PREFIX = "llm:spend:"


class UsageCounter(Protocol):
    async def total(self, month: str) -> int:
        """Spend so far this month, in millionths of a US dollar."""
        ...

    async def add(self, month: str, micro_usd: int) -> int:
        """Add spend and return the new monthly total."""
        ...


class MemoryUsageCounter:
    def __init__(self) -> None:
        self._totals: dict[str, int] = {}

    async def total(self, month: str) -> int:
        return self._totals.get(month, 0)

    async def add(self, month: str, micro_usd: int) -> int:
        self._totals[month] = self._totals.get(month, 0) + micro_usd
        return self._totals[month]


class RedisUsageCounter:
    """Shared across API and worker processes. Keys expire after 62 days."""

    def __init__(self, url: str) -> None:
        self._redis: Redis = Redis.from_url(url)

    async def total(self, month: str) -> int:
        raw = await self._redis.get(KEY_PREFIX + month)
        return int(raw) if raw else 0

    async def add(self, month: str, micro_usd: int) -> int:
        key = KEY_PREFIX + month
        total = int(await self._redis.incrby(key, micro_usd))
        await self._redis.expire(key, 62 * 24 * 3600)
        return total


def estimate_tokens(*texts: str) -> int:
    return max(1, sum(len(t) for t in texts) // CHARS_PER_TOKEN)


def month_key(now: datetime) -> str:
    return f"{now.year:04d}-{now.month:02d}"


class BudgetedLanguageModel:
    """Wraps a LanguageModel. Same protocol, plus a hard monthly cap."""

    def __init__(
        self,
        inner: LanguageModel,
        counter: UsageCounter,
        *,
        monthly_budget_usd: float,
        usd_per_million_tokens: float,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._inner = inner
        self._counter = counter
        self._cap = round(monthly_budget_usd * MICRO_USD)
        self._rate = usd_per_million_tokens
        self._clock = clock

    async def _guard(self) -> str:
        month = month_key(self._clock())
        spent = await self._counter.total(month)
        if spent >= self._cap:
            msg = (
                f"the monthly language model budget of ${self._cap / MICRO_USD:.2f} "
                "is used up; calls resume next month or when the cap is raised"
            )
            raise LlmBudgetExceededError(msg)
        return month

    async def _charge(self, month: str, *texts: str) -> None:
        micro = round(estimate_tokens(*texts) * self._rate)  # tokens * usd/1M tokens = micro usd
        await self._counter.add(month, micro)

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        month = await self._guard()
        vectors = await self._inner.embed(texts)
        await self._charge(month, *texts)
        return vectors

    async def judge_claim(self, claim: str, passages: Sequence[SourcePassage]) -> VerdictResult:
        month = await self._guard()
        result = await self._inner.judge_claim(claim, passages)
        await self._charge(month, claim, *(p.text for p in passages), result.rationale)
        return result

    async def translate(self, text: str, *, target: Language) -> str:
        month = await self._guard()
        translated = await self._inner.translate(text, target=target)
        await self._charge(month, text, translated)
        return translated
