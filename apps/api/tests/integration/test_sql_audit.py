"""Audit trail persistence on Postgres. Needs RUN_INTEGRATION=1."""

import os
from collections.abc import AsyncIterator
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from clarion_api.db.session import build_engine, build_sessionmaker
from clarion_api.db.tables import Base
from clarion_api.domain.models import AuditEvent
from clarion_api.repositories.sql import SqlAuditRepository

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


async def test_sql_audit_lists_events_for_one_subject_oldest_first(engine: AsyncEngine) -> None:
    repo = SqlAuditRepository(build_sessionmaker(engine))
    subject, other = uuid4(), uuid4()
    first = AuditEvent(actor="a", action="message.sealed", subject_id=subject, detail="none")
    second = AuditEvent(actor="b", action="message.sealed", subject_id=subject, detail="sha256:x")
    await repo.add(first)
    await repo.add(second)
    await repo.add(AuditEvent(actor="c", action="message.sealed", subject_id=other))
    await repo.add(AuditEvent(actor="d", action="message.retracted", subject_id=subject))

    sealed = await repo.list_for_subject(subject, action="message.sealed")
    assert [e.id for e in sealed] == [first.id, second.id]
    assert len(await repo.list_for_subject(subject)) == 3
