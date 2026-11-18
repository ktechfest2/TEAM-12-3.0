"""Builds every adapter once at startup from settings. Routes read it from app.state."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from importlib.resources import files

import httpx

from clarion_api.adapters.channels import Channel, build_channels
from clarion_api.adapters.llm import LanguageModel, build_language_model
from clarion_api.adapters.speech import SpeechSynthesizer, build_speech
from clarion_api.adapters.storage import ObjectStore, build_object_store
from clarion_api.config import Settings
from clarion_api.domain.models import SourcePassage
from clarion_api.repositories.base import ClaimRepository, SourceRepository
from clarion_api.repositories.memory import MemoryClaimRepository, MemorySourceRepository


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


def build_container(settings: Settings) -> Container:
    http = httpx.AsyncClient()
    return Container(
        settings=settings,
        http=http,
        llm=build_language_model(settings),
        speech=build_speech(settings),
        store=build_object_store(settings),
        channels=build_channels(settings, http),
    )


async def load_seed_sources(container: Container) -> int:
    raw = files("clarion_api.data").joinpath("seed_sources.json").read_text(encoding="utf-8")
    passages = [
        SourcePassage(
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
