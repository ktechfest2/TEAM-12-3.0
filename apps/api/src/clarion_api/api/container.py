"""Builds every adapter once at startup from settings. Routes read it from app.state."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from importlib.resources import files
from uuid import NAMESPACE_URL, uuid5

import httpx
from sqlalchemy.ext.asyncio import AsyncEngine

from clarion_api.adapters.channels import Channel, build_channels
from clarion_api.adapters.llm import LanguageModel, build_language_model
from clarion_api.adapters.speech import SpeechSynthesizer, build_speech
from clarion_api.adapters.storage import ObjectStore, build_object_store
from clarion_api.config import Settings
from clarion_api.db.session import build_engine, build_sessionmaker
from clarion_api.domain.models import SourcePassage
from clarion_api.repositories.base import (
    ClaimRepository,
    DeliveryRepository,
    MessageRepository,
    SourceRepository,
)
from clarion_api.repositories.memory import (
    MemoryClaimRepository,
    MemoryDeliveryRepository,
    MemoryMessageRepository,
    MemorySourceRepository,
)
from clarion_api.repositories.sql import (
    SqlClaimRepository,
    SqlDeliveryRepository,
    SqlMessageRepository,
    SqlSourceRepository,
)


@dataclass
class Container:
    settings: Settings
    http: httpx.AsyncClient
    llm: LanguageModel
    speech: SpeechSynthesizer
    store: ObjectStore
    channels: list[Channel]
    sources: SourceRepository = field(default_factory=MemorySourceRepository)
    claims: ClaimRepository = field(default_factory=MemoryClaimRepository)
    messages: MessageRepository = field(default_factory=MemoryMessageRepository)
    deliveries: DeliveryRepository = field(default_factory=MemoryDeliveryRepository)
    engine: AsyncEngine | None = None

    async def aclose(self) -> None:
        await self.http.aclose()
        if self.engine is not None:
            await self.engine.dispose()


def build_container(settings: Settings) -> Container:
    http = httpx.AsyncClient()
    container = Container(
        settings=settings,
        http=http,
        llm=build_language_model(settings),
        speech=build_speech(settings),
        store=build_object_store(settings),
        channels=build_channels(settings, http),
    )
    if settings.repository_backend == "sql":
        container.engine = build_engine(settings.database_url)
        sessions = build_sessionmaker(container.engine)
        container.sources = SqlSourceRepository(sessions)
        container.claims = SqlClaimRepository(sessions)
        container.messages = SqlMessageRepository(sessions)
        container.deliveries = SqlDeliveryRepository(sessions)
    return container


async def load_seed_sources(container: Container) -> int:
    raw = files("clarion_api.data").joinpath("seed_sources.json").read_text(encoding="utf-8")
    passages = [
        SourcePassage(
            id=uuid5(NAMESPACE_URL, p["url"] + p["document_title"]),
            document_title=p["document_title"],
            publisher=p["publisher"],
            url=p["url"],
            published_on=datetime.fromisoformat(p["published_on"])
            if p.get("published_on")
            else None,
            text=p["text"],
        )
        for p in json.loads(raw)["passages"]
    ]
    vectors = await container.llm.embed([p.text for p in passages])
    for passage, vector in zip(passages, vectors, strict=True):
        await container.sources.add(passage, vector)
    return len(passages)
