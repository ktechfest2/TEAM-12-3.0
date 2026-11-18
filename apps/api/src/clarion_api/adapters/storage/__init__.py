from clarion_api.adapters.storage.base import ObjectStore
from clarion_api.adapters.storage.local import LocalObjectStore
from clarion_api.config import Settings


def build_object_store(settings: Settings) -> ObjectStore:
    if settings.storage_provider == "local" or settings.is_test:
        return LocalObjectStore(settings.storage_local_dir, f"{settings.app_base_url}/media")
    # S3 compatible adapter (Supabase Storage, R2, MinIO) is task T-05.
    msg = f"STORAGE_PROVIDER '{settings.storage_provider}' adapter not built yet"
    raise RuntimeError(msg)


__all__ = ["ObjectStore", "build_object_store"]
