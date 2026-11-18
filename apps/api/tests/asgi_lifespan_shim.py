"""Runs a FastAPI app's lifespan in tests without an extra dependency."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with app.router.lifespan_context(app):
        yield
