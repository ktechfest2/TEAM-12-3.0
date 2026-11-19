"""Builds every adapter once at startup from settings. Routes read it from app.state."""

from dataclasses import dataclass, field
from importlib.resources import files

import httpx
from sqlalchemy.ext.asyncio import AsyncEngine

from clarion_api.adapters.channels import Channel, Replier, build_channels, build_replier
from clarion_api.adapters.llm import LanguageModel, build_language_model
from clarion_api.adapters.speech import SpeechSynthesizer, build_speech
from clarion_api.adapters.storage import ObjectStore, build_object_store
from clarion_api.config import Settings
from clarion_api.db.session import build_engine, build_sessionmaker
from clarion_api.repositories.base import (
    AuditRepository,
    ClaimRepository,
    DeliveryRepository,
    MessageRepository,
    SourceRepository,
    SubscriberRepository,
)
from clarion_api.repositories.memory import (
    MemoryAuditRepository,
    MemoryClaimRepository,
    MemoryDeliveryRepository,
    MemoryMessageRepository,
    MemorySourceRepository,
    MemorySubscriberRepository,
)
from clarion_api.repositories.sql import (
    SqlAuditRepository,
    SqlClaimRepository,
    SqlDeliveryRepository,
    SqlMessageRepository,
    SqlSourceRepository,
    SqlSubscriberRepository,
)
from clarion_api.services.sources import load_passages, parse_passages


@dataclass
class Container:
    settings: Settings
    http: httpx.AsyncClient
    llm: LanguageModel
    speech: SpeechSynthesizer
    store: ObjectStore
    channels: list[Channel]
    replier: Replier
    sources: SourceRepository = field(default_factory=MemorySourceRepository)
    claims: ClaimRepository = field(default_factory=MemoryClaimRepository)
    messages: MessageRepository = field(default_factory=MemoryMessageRepository)
    deliveries: DeliveryRepository = field(default_factory=MemoryDeliveryRepository)
    subscribers: SubscriberRepository = field(default_factory=MemorySubscriberRepository)
    audit: AuditRepository = field(default_factory=MemoryAuditRepository)
    engine: AsyncEngine | None = None

    async def aclose(self) -> None:
        await self.http.aclose()
        if self.engine is not None:
            await self.engine.dispose()


def build_container(settings: Settings) -> Container:
    http = httpx.AsyncClient()
    channels = build_channels(settings, http)
    container = Container(
        settings=settings,
        http=http,
        llm=build_language_model(settings),
        speech=build_speech(settings, http),
        store=build_object_store(settings, http),
        channels=channels,
        replier=build_replier(channels),
    )
    if settings.repository_backend == "sql":
        container.engine = build_engine(settings.database_url)
        sessions = build_sessionmaker(container.engine)
        container.sources = SqlSourceRepository(sessions)
        container.claims = SqlClaimRepository(sessions)
        container.messages = SqlMessageRepository(sessions)
        container.deliveries = SqlDeliveryRepository(sessions)
        container.subscribers = SqlSubscriberRepository(sessions)
        container.audit = SqlAuditRepository(sessions)
    return container


async def load_seed_sources(container: Container) -> int:
    """Load the bundled demo passages; passages already stored are skipped."""
    raw = files("clarion_api.data").joinpath("seed_sources.json").read_text(encoding="utf-8")
    report = await load_passages(parse_passages(raw), sources=container.sources, llm=container.llm)
    return report.total
