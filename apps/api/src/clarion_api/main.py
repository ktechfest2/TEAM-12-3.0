"""ASGI entry point: `uvicorn clarion_api.main:app`."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from clarion_api import __version__
from clarion_api.api.container import build_container, load_seed_sources
from clarion_api.api.routes import router
from clarion_api.config import Settings, get_settings
from clarion_api.domain.errors import (
    LlmBudgetExceededError,
    NotAuthorizedError,
    NotFoundError,
    NotPublishableError,
)
from clarion_api.observability import configure_logging, get_logger
from clarion_api.worker.broker import broker
from clarion_api.worker.runtime import use_container


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings)
    log = get_logger(__name__)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        container = build_container(settings)
        app.state.container = container
        use_container(container)
        await broker.startup()
        seeded = await load_seed_sources(container)
        log.info("startup", env=settings.app_env.value, seeded_sources=seeded)
        yield
        await broker.shutdown()
        use_container(None)
        await container.aclose()

    app = FastAPI(title="Clarion API", version=__version__, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)

    @app.exception_handler(NotFoundError)
    async def not_found(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(NotPublishableError)
    async def not_publishable(_: Request, exc: NotPublishableError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(NotAuthorizedError)
    async def not_authorized(_: Request, exc: NotAuthorizedError) -> JSONResponse:
        return JSONResponse(
            status_code=401, content={"detail": str(exc)}, headers={"WWW-Authenticate": "Bearer"}
        )

    @app.exception_handler(LlmBudgetExceededError)
    async def over_budget(_: Request, exc: LlmBudgetExceededError) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    return app


app = create_app()
