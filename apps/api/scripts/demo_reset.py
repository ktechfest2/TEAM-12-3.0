"""Reset the demo workspace to known data.

Usage: make demo-reset CONFIRM=1     (needs REPOSITORY_BACKEND=sql)

Deletes claims, messages, reviews, deliveries and subscribers, keeps and refreshes the
official sources, then queues the demo claims as drafts for the reviewer.
"""

import asyncio
import sys

from clarion_api.api.container import build_container, load_seed_sources
from clarion_api.config import get_settings
from clarion_api.db.session import build_sessionmaker
from clarion_api.repositories.sql import clear_workspace_data
from clarion_api.services.demo import LIVE_CLAIM, ensure_reset_allowed, queue_demo_claims


async def run(confirmed: bool) -> None:
    settings = get_settings()
    ensure_reset_allowed(settings, confirmed=confirmed)
    container = build_container(settings)
    if container.engine is None:
        msg = "the sql backend did not create an engine"
        raise RuntimeError(msg)
    try:
        await clear_workspace_data(build_sessionmaker(container.engine))
        sources = await load_seed_sources(container)
        drafts = await queue_demo_claims(
            claims=container.claims,
            sources=container.sources,
            messages=container.messages,
            llm=container.llm,
        )
    finally:
        await container.aclose()
    print(f"demo reset: {sources} sources, {len(drafts)} drafts queued")  # noqa: T201
    print(f"type this one live: {LIVE_CLAIM.text}")  # noqa: T201


def main() -> None:
    asyncio.run(run(confirmed="--yes" in sys.argv[1:]))


if __name__ == "__main__":
    main()
