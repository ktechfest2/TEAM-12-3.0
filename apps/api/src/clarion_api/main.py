"""ASGI entry point: `uvicorn clarion_api.main:app`."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from clarion_api import __version__
from clarion_api.api.container import build_container, load_seed_sources
from clarion_api.api.routes import router
from clarion_api.config import Settings, get_settings
from clarion_api.observability import configure_logging, get_logger


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings)
    log = get_logger(__name__)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        container = build_container(settings)
        app.state.container = container
        seeded = await load_seed_sources(container)
        log.info("startup", env=settings.app_env.value, seeded_sources=seeded)
        yield
        await container.http.aclose()

    app = FastAPI(title="Clarion API", version=__version__, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()
