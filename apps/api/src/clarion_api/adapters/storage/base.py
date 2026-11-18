from typing import Protocol


class ObjectStore(Protocol):
    async def put(self, key: str, data: bytes, *, content_type: str) -> str:
        """Store bytes under key and return a public URL."""
        ...
