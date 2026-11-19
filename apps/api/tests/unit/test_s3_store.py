from datetime import UTC, datetime

import httpx
import pytest

from clarion_api.adapters.storage import build_object_store
from clarion_api.adapters.storage.s3 import (
    S3ObjectStore,
    authorization_header,
    sha256_hex,
    signing_key,
)
from clarion_api.config import AppEnv, Settings

# Published AWS Signature Version 4 examples (documentation and the "get-vanilla" test case).
EXAMPLE_SECRET = "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY"  # noqa: S105
EXAMPLE_ACCESS = "AKIDEXAMPLE"
EMPTY_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_signing_key_matches_the_published_example() -> None:
    key = signing_key(EXAMPLE_SECRET, "20150830", "us-east-1", "iam")
    assert key.hex() == "c4afb1cc5771d871763a393e44b703571b55cc28424d1a5e86da6ed3c154a4b9"


def test_authorization_matches_the_published_get_vanilla_case() -> None:
    header = authorization_header(
        method="GET",
        canonical_uri="/",
        query="",
        headers={"Host": "example.amazonaws.com", "X-Amz-Date": "20150830T123600Z"},
        payload_hash=EMPTY_HASH,
        access_key=EXAMPLE_ACCESS,
        secret_key=EXAMPLE_SECRET,
        region="us-east-1",
        service="service",
        amz_date="20150830T123600Z",
    )
    assert header == (
        "AWS4-HMAC-SHA256 Credential=AKIDEXAMPLE/20150830/us-east-1/service/aws4_request, "
        "SignedHeaders=host;x-amz-date, "
        "Signature=5fa00fa31553b73ebf1942676e86291e8372ff2a2260956d9b8aae1d763fbf31"
    )


def _store(client: httpx.AsyncClient, *, public: str | None = None) -> S3ObjectStore:
    return S3ObjectStore(
        client=client,
        endpoint_url="https://storage.example.test/s3/",
        bucket="clarion-media",
        region="eu-west-1",
        access_key_id="ACCESS",
        secret_access_key="SECRET",
        public_base_url=public,
        clock=lambda: datetime(2027, 1, 15, 8, 30, 0, tzinfo=UTC),
    )


async def test_put_sends_a_signed_request_and_returns_the_object_url() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        url = await _store(client).put("cards/a b.png", b"png-bytes", content_type="image/png")

    [request] = seen
    assert request.method == "PUT"
    assert str(request.url) == "https://storage.example.test/s3/clarion-media/cards/a%20b.png"
    assert request.content == b"png-bytes"
    assert request.headers["content-type"] == "image/png"
    assert request.headers["x-amz-date"] == "20270115T083000Z"
    assert request.headers["x-amz-content-sha256"] == sha256_hex(b"png-bytes")
    auth = request.headers["authorization"]
    assert auth.startswith("AWS4-HMAC-SHA256 Credential=ACCESS/20270115/eu-west-1/s3/aws4_request")
    assert "SignedHeaders=content-type;host;x-amz-content-sha256;x-amz-date" in auth
    assert url == "https://storage.example.test/s3/clarion-media/cards/a%20b.png"


async def test_public_base_url_is_used_for_the_returned_link() -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _: httpx.Response(200))
    ) as client:
        url = await _store(client, public="https://cdn.example.test/media/").put(
            "voice/yo.ogg", b"x", content_type="audio/ogg"
        )
    assert url == "https://cdn.example.test/media/voice/yo.ogg"


async def test_failed_upload_raises() -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _: httpx.Response(403))
    ) as client:
        with pytest.raises(httpx.HTTPStatusError):
            await _store(client).put("k", b"x", content_type="text/plain")


def test_factory_builds_the_s3_store_and_demands_credentials() -> None:
    complete = Settings(  # type: ignore[call-arg]
        app_env=AppEnv.DEVELOPMENT,
        storage_provider="s3",
        storage_endpoint_url="https://storage.example.test/s3",
        storage_access_key_id="id",  # type: ignore[arg-type]
        storage_secret_access_key="secret",  # type: ignore[arg-type]
        _env_file=None,
    )
    assert isinstance(build_object_store(complete), S3ObjectStore)

    missing = Settings(app_env=AppEnv.DEVELOPMENT, storage_provider="s3", _env_file=None)  # type: ignore[call-arg]
    with pytest.raises(RuntimeError, match="STORAGE_ENDPOINT_URL"):
        build_object_store(missing)
