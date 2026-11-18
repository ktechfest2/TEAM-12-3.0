from taskiq import AsyncBroker, InMemoryBroker
from taskiq_redis import ListQueueBroker

from clarion_api.config import get_settings


def build_broker() -> AsyncBroker:
    settings = get_settings()
    if settings.is_test:
        return InMemoryBroker()
    return ListQueueBroker(url=settings.redis_url)


broker = build_broker()
