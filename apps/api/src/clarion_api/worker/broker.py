"""Background jobs (channel sends, media rendering).

Run with: taskiq worker clarion_api.worker.broker:broker clarion_api.worker.tasks
"""

from taskiq import AsyncBroker, InMemoryBroker
from taskiq_redis import ListQueueBroker

from clarion_api.config import get_settings


def build_broker() -> AsyncBroker:
    settings = get_settings()
    if settings.is_test:
        # Runs each job inside kiq(), so tests see receipts as soon as the request returns.
        return InMemoryBroker(await_inplace=True)
    return ListQueueBroker(url=settings.redis_url)


broker = build_broker()
