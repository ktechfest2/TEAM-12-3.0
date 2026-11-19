"""Runs the shared repository contract against Postgres. Needs RUN_INTEGRATION=1."""

import os
from collections.abc import AsyncIterator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from clarion_api.db.session import build_engine, build_sessionmaker
from clarion_api.db.tables import Base
from clarion_api.repositories.sql import SqlClaimRepository, SqlSourceRepository
from tests.support import repository_contract as contract

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


async def test_sql_source_add_and_get(engine: AsyncEngine) -> None:
    await contract.check_source_add_and_get(SqlSourceRepository(build_sessionmaker(engine)))


async def test_sql_source_get_missing_returns_none(engine: AsyncEngine) -> None:
    await contract.check_source_get_missing(SqlSourceRepository(build_sessionmaker(engine)))


async def test_sql_source_search_orders_by_similarity(engine: AsyncEngine) -> None:
    repo = SqlSourceRepository(build_sessionmaker(engine))
    await contract.check_source_search_orders_by_similarity(repo)


async def test_sql_source_search_respects_limit(engine: AsyncEngine) -> None:
    await contract.check_source_search_respects_limit(
        SqlSourceRepository(build_sessionmaker(engine))
    )


async def test_sql_claims_add_get_and_list(engine: AsyncEngine) -> None:
    await contract.check_claim_add_get_and_list(SqlClaimRepository(build_sessionmaker(engine)))
