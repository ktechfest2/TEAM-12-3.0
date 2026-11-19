import os
from collections.abc import AsyncIterator

os.environ["APP_ENV"] = "test"  # before any clarion_api import reads settings

import httpx
import pytest

from clarion_api.adapters.channels.console import ConsoleChannel
from clarion_api.api.container import Container
from clarion_api.config import AppEnv, Settings
from clarion_api.main import create_app
from tests.asgi_lifespan_shim import lifespan


@pytest.fixture
def settings() -> Settings:
    return Settings(app_env=AppEnv.TEST, _env_file=None)  # type: ignore[call-arg]


@pytest.fixture
async def app_and_client(
    settings: Settings,
) -> AsyncIterator[tuple[Container, httpx.AsyncClient]]:
    app = create_app(settings)
    async with lifespan(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
            yield app.state.container, c


@pytest.fixture
def client(app_and_client: tuple[Container, httpx.AsyncClient]) -> httpx.AsyncClient:
    return app_and_client[1]


@pytest.fixture
def container(app_and_client: tuple[Container, httpx.AsyncClient]) -> Container:
    return app_and_client[0]


@pytest.fixture
def console(container: Container) -> ConsoleChannel:
    [channel] = container.channels
    assert isinstance(channel, ConsoleChannel)
    return channel
