import json
from importlib.resources import files
from pathlib import Path

import pytest

from clarion_api.adapters.llm.fake import FakeLanguageModel
from clarion_api.repositories.memory import MemorySourceRepository
from clarion_api.services.sources import (
    load_passages,
    parse_passages,
    passage_id,
    read_passages,
)

RECORD = {
    "document_title": "INEC statement",
    "publisher": "INEC",
    "url": "https://example.org/statement",
    "published_on": "2026-07-29",
    "text": "The commission did not issue the timetable.",
}


def _file(tmp_path: Path, records: list[dict[str, str]]) -> Path:
    path = tmp_path / "passages.json"
    path.write_text(json.dumps({"passages": records}), encoding="utf-8")
    return path


async def test_loading_adds_passages_that_search_can_find(tmp_path: Path) -> None:
    sources = MemorySourceRepository()
    llm = FakeLanguageModel(dimensions=64)
    report = await load_passages(read_passages(_file(tmp_path, [RECORD])), sources=sources, llm=llm)
    assert (report.added, report.skipped) == (1, 0)
    [vector] = await llm.embed(["the commission did not issue the timetable"])
    [found] = await sources.search(vector, limit=3)
    assert found.id == passage_id(RECORD["url"], RECORD["text"])


async def test_loading_the_same_file_twice_skips_every_duplicate(tmp_path: Path) -> None:
    sources = MemorySourceRepository()
    llm = FakeLanguageModel(dimensions=64)
    passages = read_passages(_file(tmp_path, [RECORD]))
    await load_passages(passages, sources=sources, llm=llm)
    again = await load_passages(passages, sources=sources, llm=llm)
    assert (again.added, again.skipped) == (0, 1)


async def test_duplicates_inside_one_file_are_loaded_once(tmp_path: Path) -> None:
    sources = MemorySourceRepository()
    report = await load_passages(
        read_passages(_file(tmp_path, [RECORD, dict(RECORD)])),
        sources=sources,
        llm=FakeLanguageModel(dimensions=64),
    )
    assert (report.added, report.skipped) == (1, 1)


async def test_same_url_with_different_text_is_a_different_passage(tmp_path: Path) -> None:
    other = {**RECORD, "text": "A second paragraph from the same page."}
    report = await load_passages(
        read_passages(_file(tmp_path, [RECORD, other])),
        sources=MemorySourceRepository(),
        llm=FakeLanguageModel(dimensions=64),
    )
    assert report.added == 2


def test_a_record_missing_a_field_is_rejected() -> None:
    broken = {key: value for key, value in RECORD.items() if key != "url"}
    with pytest.raises(KeyError):
        parse_passages(json.dumps({"passages": [broken]}))


def test_the_bundled_seed_file_parses() -> None:
    raw = files("clarion_api.data").joinpath("seed_sources.json").read_text(encoding="utf-8")
    assert len(parse_passages(raw)) >= 1
