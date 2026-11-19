"""Subscriber persistence on Postgres. Needs RUN_INTEGRATION=1."""

import os
from collections.abc import AsyncIterator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from clarion_api.db.session import build_engine, build_sessionmaker
from clarion_api.db.tables import Base
from clarion_api.domain.enums import ChannelKind, Language
from clarion_api.domain.models import Subscriber
from clarion_api.repositories.sql import SqlSubscriberRepository

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(os.getenv("RUN_INTEGRATION") != "1", reason="set RUN_INTEGRATION=1"),
]


@pytest.fixture
async def engine() -> AsyncIterator[AsyncEngine]:
    engine = build_engine(os.environ["DATABASE_URL"])
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


async def test_sql_subscriber_upsert_get_and_remove(engine: AsyncEngine) -> None:
    repo = SqlSubscriberRepository(build_sessionmaker(engine))
    first = Subscriber(channel=ChannelKind.TELEGRAM, address_hash="h1", language=Language.YORUBA)
    saved = await repo.upsert(first)
    again = await repo.upsert(first.model_copy(update={"language": Language.IGBO}))

    assert again.id == saved.id
    assert again.language is Language.IGBO
    assert again.consented_at == saved.consented_at
    assert await repo.count() == 1
    assert await repo.get(ChannelKind.TELEGRAM, "h1") is not None
    assert await repo.get(ChannelKind.SMS, "h1") is None
    assert await repo.remove(ChannelKind.TELEGRAM, "h1")
    assert not await repo.remove(ChannelKind.TELEGRAM, "h1")
    assert await repo.count() == 0
