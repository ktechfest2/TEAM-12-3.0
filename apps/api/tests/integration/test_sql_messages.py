"""Message and delivery persistence round trips on Postgres. Needs RUN_INTEGRATION=1."""

import os
from collections.abc import AsyncIterator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from clarion_api.db.session import build_engine, build_sessionmaker
from clarion_api.db.tables import Base
from clarion_api.domain.enums import ChannelKind, DeliveryStatus, Language, ReviewStatus
from clarion_api.domain.models import Claim, Delivery
from clarion_api.repositories.sql import (
    SqlClaimRepository,
    SqlDeliveryRepository,
    SqlMessageRepository,
    SqlSourceRepository,
    clear_workspace_data,
)
from tests.factories import approved_message
from tests.support.repository_contract import unit_vector

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


async def test_sql_message_round_trip_keeps_review_localisations_and_seal(
    engine: AsyncEngine,
) -> None:
    sessions = build_sessionmaker(engine)
    message = approved_message()
    assert message.passage is not None
    await SqlSourceRepository(sessions).add(message.passage, unit_vector(0))
    await SqlClaimRepository(sessions).add(Claim(id=message.claim_id, text="a claim"))
    repo = SqlMessageRepository(sessions)

    await repo.save(message)
    loaded = await repo.get(message.id)

    assert loaded is not None
    assert loaded.verdict is message.verdict
    assert loaded.passage is not None
    assert loaded.passage.id == message.passage.id
    assert loaded.review is not None
    assert loaded.review.status is ReviewStatus.APPROVED
    assert [(loc.language, loc.approved_by) for loc in loaded.localisations] == [
        (Language.YORUBA, "native-yo")
    ]
    assert loaded.integrity_hash == message.integrity_hash
    assert await repo.latest_integrity_hash() == message.integrity_hash
    assert await repo.latest_integrity_hash(excluding=message.id) is None


async def test_sql_message_save_drops_removed_localisations(engine: AsyncEngine) -> None:
    sessions = build_sessionmaker(engine)
    message = approved_message()
    assert message.passage is not None
    await SqlSourceRepository(sessions).add(message.passage, unit_vector(0))
    await SqlClaimRepository(sessions).add(Claim(id=message.claim_id, text="a claim"))
    repo = SqlMessageRepository(sessions)
    await repo.save(message)

    await repo.save(message.model_copy(update={"localisations": (), "integrity_hash": None}))

    loaded = await repo.get(message.id)
    assert loaded is not None
    assert loaded.localisations == ()
    assert loaded.integrity_hash is None


async def test_sql_delivery_save_get_and_list(engine: AsyncEngine) -> None:
    sessions = build_sessionmaker(engine)
    message = approved_message()
    assert message.passage is not None
    await SqlSourceRepository(sessions).add(message.passage, unit_vector(0))
    await SqlClaimRepository(sessions).add(Claim(id=message.claim_id, text="a claim"))
    await SqlMessageRepository(sessions).save(message)
    repo = SqlDeliveryRepository(sessions)
    delivery = Delivery(
        message_id=message.id, channel=ChannelKind.TELEGRAM, language=Language.ENGLISH
    )

    await repo.save(delivery)
    await repo.save(delivery.model_copy(update={"status": DeliveryStatus.SENT, "external_id": "9"}))

    loaded = await repo.get(delivery.id)
    assert loaded is not None
    assert loaded.status is DeliveryStatus.SENT
    assert [d.id for d in await repo.list_for_message(message.id)] == [delivery.id]
    assert len(await repo.list_recent(limit=5)) == 1


async def test_clear_workspace_data_keeps_official_sources(engine: AsyncEngine) -> None:
    sessions = build_sessionmaker(engine)
    message = approved_message()
    assert message.passage is not None
    sources = SqlSourceRepository(sessions)
    await sources.add(message.passage, unit_vector(0))
    await SqlClaimRepository(sessions).add(Claim(id=message.claim_id, text="a claim"))
    messages = SqlMessageRepository(sessions)
    await messages.save(message)

    await clear_workspace_data(sessions)

    assert await messages.get(message.id) is None
    assert await SqlClaimRepository(sessions).get(message.claim_id) is None
    assert await sources.get(message.passage.id) is not None
