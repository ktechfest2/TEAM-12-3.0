"""Needs RUN_INTEGRATION=1 and REDIS_URL pointing at a disposable Redis."""

import os
from uuid import uuid4

import pytest

from clarion_api.adapters.llm.budget import RedisUsageCounter

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(os.getenv("RUN_INTEGRATION") != "1", reason="set RUN_INTEGRATION=1"),
]


async def test_redis_counter_accumulates_per_month() -> None:
    counter = RedisUsageCounter(os.environ["REDIS_URL"])
    month = f"test-{uuid4()}"
    assert await counter.total(month) == 0
    assert await counter.add(month, 40) == 40
    assert await counter.add(month, 2) == 42
    assert await counter.total(month) == 42
