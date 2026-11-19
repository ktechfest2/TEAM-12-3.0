import httpx

from clarion_api.adapters.storage.base import ObjectStore
from clarion_api.adapters.storage.local import LocalObjectStore
from clarion_api.config import Settings

DEFAULT_REGION = "us-east-1"


def build_object_store(settings: Settings, client: httpx.AsyncClient | None = None) -> ObjectStore:
    if settings.storage_provider == "local" or settings.is_test:
        return LocalObjectStore(settings.storage_local_dir, f"{settings.app_base_url}/media")
    if settings.storage_provider == "s3":
        from clarion_api.adapters.storage.s3 import S3ObjectStore  # noqa: PLC0415

        if not (
            settings.storage_endpoint_url
            and settings.storage_access_key_id
            and settings.storage_secret_access_key
        ):
            msg = (
                "STORAGE_ENDPOINT_URL, STORAGE_ACCESS_KEY_ID and STORAGE_SECRET_ACCESS_KEY "
                "are required when STORAGE_PROVIDER=s3"
            )
            raise RuntimeError(msg)
        return S3ObjectStore(
            client=client or httpx.AsyncClient(),
            endpoint_url=settings.storage_endpoint_url,
            bucket=settings.storage_bucket,
            region=settings.storage_region or DEFAULT_REGION,
            access_key_id=settings.storage_access_key_id.get_secret_value(),
            secret_access_key=settings.storage_secret_access_key.get_secret_value(),
            public_base_url=settings.storage_public_base_url,
        )
    msg = f"unknown STORAGE_PROVIDER: {settings.storage_provider}"
    raise RuntimeError(msg)


__all__ = ["ObjectStore", "build_object_store"]
