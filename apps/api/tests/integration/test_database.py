"""Runs only with RUN_INTEGRATION=1 and a Postgres with pgvector (CI provides one)."""

import os

import pytest
from sqlalchemy import text

from clarion_api.db.session import build_engine

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(os.getenv("RUN_INTEGRATION") != "1", reason="set RUN_INTEGRATION=1"),
]


async def test_pgvector_extension_is_available() -> None:
    engine = build_engine(os.environ["DATABASE_URL"])
    async with engine.connect() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        version = await conn.scalar(
            text("SELECT extversion FROM pg_extension WHERE extname='vector'")
        )
    await engine.dispose()
    assert version
