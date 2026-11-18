import asyncio
from pathlib import Path


class LocalObjectStore:
    """Writes to a local folder. Development and tests only."""

    def __init__(self, root: str, public_base_url: str) -> None:
        self._root = Path(root)
        self._public = public_base_url.rstrip("/")

    async def put(self, key: str, data: bytes, *, content_type: str) -> str:
        path = self._root / key
        await asyncio.to_thread(path.parent.mkdir, parents=True, exist_ok=True)
        await asyncio.to_thread(path.write_bytes, data)
        return f"{self._public}/{key}"
