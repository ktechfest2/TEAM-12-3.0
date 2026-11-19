import os
from collections.abc import AsyncIterator
from dataclasses import dataclass

os.environ["APP_ENV"] = "test"  # before any clarion_api import reads settings

import httpx
import pytest
from pydantic import SecretStr

from clarion_api.adapters.channels.console import ConsoleChannel
from clarion_api.api.container import Container
from clarion_api.config import AppEnv, Settings
from clarion_api.main import create_app
from tests.asgi_lifespan_shim import lifespan

INVITE_CODE = "test-invite-code"


@dataclass
class Running:
    container: Container
    anonymous: httpx.AsyncClient
    reviewer: httpx.AsyncClient


@pytest.fixture
def settings() -> Settings:
    return Settings(  # type: ignore[call-arg]
        app_env=AppEnv.TEST,
        auth_reviewer_invite_code=SecretStr(INVITE_CODE),
        auth_jwt_secret=SecretStr("test-signing-secret"),
        _env_file=None,
    )


@pytest.fixture
async def running(settings: Settings) -> AsyncIterator[Running]:
    app = create_app(settings)
    async with lifespan(app):
        transport = httpx.ASGITransport(app=app)
        async with (
            httpx.AsyncClient(transport=transport, base_url="http://test") as anonymous,
            httpx.AsyncClient(transport=transport, base_url="http://test") as reviewer,
        ):
            issued = await anonymous.post(
                "/auth/tokens", json={"invite_code": INVITE_CODE, "reviewer_name": "reviewer-1"}
            )
            reviewer.headers["Authorization"] = f"Bearer {issued.json()['access_token']}"
            yield Running(app.state.container, anonymous, reviewer)


@pytest.fixture
def client(running: Running) -> httpx.AsyncClient:
    """A client that carries a valid reviewer token."""
    return running.reviewer


@pytest.fixture
def anonymous_client(running: Running) -> httpx.AsyncClient:
    return running.anonymous


@pytest.fixture
def container(running: Running) -> Container:
    return running.container


@pytest.fixture
def console(container: Container) -> ConsoleChannel:
    [channel] = container.channels
    assert isinstance(channel, ConsoleChannel)
    return channel
