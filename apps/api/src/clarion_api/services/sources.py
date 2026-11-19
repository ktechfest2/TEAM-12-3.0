"""Loads official passages into the source repository.

A passage is identified by its URL and text, so loading the same file twice (or
two files that share a passage) never creates duplicates.
"""

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from clarion_api.adapters.llm.base import LanguageModel
from clarion_api.domain.models import SourcePassage
from clarion_api.repositories.base import SourceRepository


@dataclass(frozen=True)
class LoadReport:
    added: int
    skipped: int

    @property
    def total(self) -> int:
        return self.added + self.skipped


def passage_id(url: str, text: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"{url}\n{text}")


def passage_from_record(record: Mapping[str, Any]) -> SourcePassage:
    url = str(record["url"])
    text = str(record["text"])
    published = record.get("published_on")
    return SourcePassage(
        id=passage_id(url, text),
        document_title=str(record["document_title"]),
        publisher=str(record["publisher"]),
        url=url,
        published_on=datetime.fromisoformat(str(published)) if published else None,
        text=text,
    )


def parse_passages(raw: str) -> list[SourcePassage]:
    """Parse JSON shaped like `{"passages": [{document_title, publisher, url, text}]}`."""
    return [passage_from_record(record) for record in json.loads(raw)["passages"]]


def read_passages(path: Path) -> list[SourcePassage]:
    return parse_passages(path.read_text(encoding="utf-8"))


async def load_passages(
    passages: Iterable[SourcePassage], *, sources: SourceRepository, llm: LanguageModel
) -> LoadReport:
    """Embed and store every passage that is not already stored."""
    fresh: list[SourcePassage] = []
    seen: set[UUID] = set()
    skipped = 0
    for passage in passages:
        if passage.id in seen or await sources.get(passage.id) is not None:
            skipped += 1
            continue
        seen.add(passage.id)
        fresh.append(passage)
    if fresh:
        vectors = await llm.embed([p.text for p in fresh])
        for passage, vector in zip(fresh, vectors, strict=True):
            await sources.add(passage, vector)
    return LoadReport(added=len(fresh), skipped=skipped)
