"""S3 compatible object store over plain HTTPS (AWS Signature Version 4, path style).

Works with Supabase Storage, Cloudflare R2, MinIO and AWS S3 through the S3
protocol. It uses httpx and the standard library, so there is no vendor SDK.
"""

import hashlib
import hmac
from collections.abc import Callable, Mapping
from datetime import datetime
from urllib.parse import quote, urlsplit

import httpx

from clarion_api.domain.models import utc_now

ALGORITHM = "AWS4-HMAC-SHA256"


def _hmac(key: bytes, message: str) -> bytes:
    return hmac.new(key, message.encode("utf-8"), hashlib.sha256).digest()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def signing_key(secret_key: str, date: str, region: str, service: str) -> bytes:
    """Derive the per-day signing key: HMAC chain over date, region, service and the terminator."""
    k_date = _hmac(f"AWS4{secret_key}".encode(), date)
    k_region = _hmac(k_date, region)
    k_service = _hmac(k_region, service)
    return _hmac(k_service, "aws4_request")


def authorization_header(
    *,
    method: str,
    canonical_uri: str,
    query: str,
    headers: Mapping[str, str],
    payload_hash: str,
    access_key: str,
    secret_key: str,
    region: str,
    service: str,
    amz_date: str,
) -> str:
    """Build the Authorization header value for the given request parts.

    `headers` are exactly the headers to sign (lower or mixed case); they must include
    `host` and `x-amz-date`.
    """
    date = amz_date[:8]
    normalised = {name.lower(): " ".join(value.split()) for name, value in headers.items()}
    names = sorted(normalised)
    canonical_headers = "".join(f"{name}:{normalised[name]}\n" for name in names)
    signed_headers = ";".join(names)
    canonical_request = "\n".join(
        [method, canonical_uri, query, canonical_headers, signed_headers, payload_hash]
    )
    scope = f"{date}/{region}/{service}/aws4_request"
    string_to_sign = "\n".join(
        [ALGORITHM, amz_date, scope, sha256_hex(canonical_request.encode("utf-8"))]
    )
    key = signing_key(secret_key, date, region, service)
    signature = hmac.new(key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
    return (
        f"{ALGORITHM} Credential={access_key}/{scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )


class S3ObjectStore:
    def __init__(
        self,
        *,
        client: httpx.AsyncClient,
        endpoint_url: str,
        bucket: str,
        region: str,
        access_key_id: str,
        secret_access_key: str,
        public_base_url: str | None = None,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._client = client
        self._endpoint = endpoint_url.rstrip("/")
        self._host = urlsplit(self._endpoint).netloc
        self._bucket = bucket
        self._region = region
        self._access_key = access_key_id
        self._secret_key = secret_access_key
        self._public = public_base_url.rstrip("/") if public_base_url else None
        self._clock = clock

    def _object_path(self, key: str) -> str:
        return f"/{quote(self._bucket, safe='')}/{quote(key.lstrip('/'), safe='/-_.~')}"

    def public_url(self, key: str) -> str:
        if self._public:
            return f"{self._public}/{quote(key.lstrip('/'), safe='/-_.~')}"
        return f"{self._endpoint}{self._object_path(key)}"

    async def put(self, key: str, data: bytes, *, content_type: str) -> str:
        path = self._object_path(key)
        amz_date = self._clock().strftime("%Y%m%dT%H%M%SZ")
        payload_hash = sha256_hex(data)
        signed = {
            "content-type": content_type,
            "host": self._host,
            "x-amz-content-sha256": payload_hash,
            "x-amz-date": amz_date,
        }
        authorization = authorization_header(
            method="PUT",
            canonical_uri=path,
            query="",
            headers=signed,
            payload_hash=payload_hash,
            access_key=self._access_key,
            secret_key=self._secret_key,
            region=self._region,
            service="s3",
            amz_date=amz_date,
        )
        response = await self._client.put(
            f"{self._endpoint}{path}",
            content=data,
            headers={
                "Content-Type": content_type,
                "x-amz-content-sha256": payload_hash,
                "x-amz-date": amz_date,
                "Authorization": authorization,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        return self.public_url(key)

    async def exists(self, key: str) -> bool:
        path = self._object_path(key)
        amz_date = self._clock().strftime("%Y%m%dT%H%M%SZ")
        payload_hash = sha256_hex(b"")
        signed = {
            "host": self._host,
            "x-amz-content-sha256": payload_hash,
            "x-amz-date": amz_date,
        }
        authorization = authorization_header(
            method="HEAD",
            canonical_uri=path,
            query="",
            headers=signed,
            payload_hash=payload_hash,
            access_key=self._access_key,
            secret_key=self._secret_key,
            region=self._region,
            service="s3",
            amz_date=amz_date,
        )
        response = await self._client.head(
            f"{self._endpoint}{path}",
            headers={
                "x-amz-content-sha256": payload_hash,
                "x-amz-date": amz_date,
                "Authorization": authorization,
            },
            timeout=30.0,
        )
        if response.status_code == 404:
            return False
        response.raise_for_status()
        return True
