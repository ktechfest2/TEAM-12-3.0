from typing import Protocol


class ObjectStore(Protocol):
    async def put(self, key: str, data: bytes, *, content_type: str) -> str:
        """Store bytes under key and return a public URL."""
        ...

    async def exists(self, key: str) -> bool:
        """True when something is already stored under key."""
        ...

    def public_url(self, key: str) -> str:
        """The public URL a stored key is (or would be) served at."""
        ...
