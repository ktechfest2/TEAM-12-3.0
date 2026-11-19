import json

import httpx
import pytest

from clarion_api.adapters.channels import build_channels
from clarion_api.adapters.channels.textbee import TextBeeChannel
from clarion_api.adapters.channels.x_posts import XChannel
from clarion_api.config import Settings


async def test_textbee_sends_to_listed_numbers_only() -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["key"] = request.headers["x-api-key"]
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"data": {"success": True, "smsBatchId": "b-1"}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        channel = TextBeeChannel(
            api_key="k", recipients=["+2348000000001"], client=client, device_id="d1"
        )
        assert await channel.send_text("hello") == "b-1"
    assert seen["key"] == "k"
    assert seen["body"] == {"recipients": ["+2348000000001"], "message": "hello", "deviceId": "d1"}


async def test_textbee_error_raises() -> None:
    handler = lambda _: httpx.Response(401, json={"message": "bad key"})  # noqa: E731
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        channel = TextBeeChannel(api_key="k", recipients=["+2348000000001"], client=client)
        with pytest.raises(httpx.HTTPStatusError):
            await channel.send_text("hello")


async def test_x_posts_and_returns_post_id() -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers["authorization"]
        seen["body"] = json.loads(request.content)
        return httpx.Response(201, json={"data": {"id": "123", "text": "hi"}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        assert await XChannel(access_token="tok", client=client).send_text("hi") == "123"
    assert seen["auth"] == "Bearer tok"
    assert seen["body"] == {"text": "hi"}


async def test_x_error_carries_detail() -> None:
    handler = lambda _: httpx.Response(403, json={"detail": "not allowed"})  # noqa: E731
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(RuntimeError, match="not allowed"):
            await XChannel(access_token="tok", client=client).send_text("hi")


def test_factory_enables_textbee_and_x_only_when_configured() -> None:

    settings = Settings(
        app_env="development",
        channel_sms_provider="textbee",
        channel_sms_api_key="k",
        channel_sms_recipients="+2348000000001, +2348000000002",
        channel_x_access_token="tok",
    )
    kinds = {c.kind.value for c in build_channels(settings, httpx.AsyncClient())}
    assert kinds == {"sms", "x"}
    no_numbers = settings.model_copy(update={"channel_sms_recipients": ""})
    assert {c.kind.value for c in build_channels(no_numbers, httpx.AsyncClient())} == {"x"}
