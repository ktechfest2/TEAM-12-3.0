"""Load official passages from a JSON file into the active repository.

Usage: make seed-sources FILE=path/to/passages.json   (REPOSITORY_BACKEND=sql to persist)
"""

import asyncio
import sys
from pathlib import Path

from clarion_api.api.container import build_container
from clarion_api.config import get_settings
from clarion_api.services.sources import load_passages, read_passages


async def run(path: Path) -> None:
    container = build_container(get_settings())
    try:
        report = await load_passages(
            read_passages(path), sources=container.sources, llm=container.llm
        )
    finally:
        await container.aclose()
    print(f"loaded {report.added} passages, skipped {report.skipped} duplicates")  # noqa: T201


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: seed_sources.py <passages.json>", file=sys.stderr)  # noqa: T201
        raise SystemExit(2)
    asyncio.run(run(Path(sys.argv[1])))


if __name__ == "__main__":
    main()
