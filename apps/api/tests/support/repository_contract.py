"""Behaviour every repository implementation must satisfy. Run for memory and sql."""

from clarion_api.domain.enums import ChannelKind, Language
from clarion_api.domain.models import Claim, SourcePassage
from clarion_api.repositories.base import ClaimRepository, SourceRepository

DIMENSIONS = 768


def unit_vector(axis: int, *, mix: tuple[int, float] | None = None) -> list[float]:
    vec = [0.0] * DIMENSIONS
    vec[axis] = 1.0
    if mix:
        vec[mix[0]] = mix[1]
    return vec


def make_passage(title: str) -> SourcePassage:
    return SourcePassage(
        document_title=title,
        publisher="INEC",
        url="https://example.org/doc",
        text=f"Text of {title}",
    )


async def check_source_add_and_get(repo: SourceRepository) -> None:
    passage = make_passage("Timetable")
    await repo.add(passage, unit_vector(0))
    loaded = await repo.get(passage.id)
    assert loaded is not None
    assert loaded.id == passage.id
    assert loaded.document_title == "Timetable"
    assert str(loaded.url) == str(passage.url)


async def check_source_get_missing(repo: SourceRepository) -> None:
    assert await repo.get(make_passage("x").id) is None


async def check_source_search_orders_by_similarity(repo: SourceRepository) -> None:
    near, mid, far = make_passage("near"), make_passage("mid"), make_passage("far")
    await repo.add(far, unit_vector(2))
    await repo.add(mid, unit_vector(0, mix=(1, 1.0)))
    await repo.add(near, unit_vector(0, mix=(1, 0.1)))
    found = await repo.search(unit_vector(0), limit=5)
    assert [p.document_title for p in found] == ["near", "mid"]


async def check_source_search_respects_limit(repo: SourceRepository) -> None:
    await repo.add(make_passage("a"), unit_vector(0))
    await repo.add(make_passage("b"), unit_vector(0, mix=(1, 0.2)))
    assert len(await repo.search(unit_vector(0), limit=1)) == 1


async def check_claim_add_get_and_list(repo: ClaimRepository) -> None:
    first = Claim(text="first claim", language=Language.YORUBA, submitted_via=ChannelKind.TELEGRAM)
    second = Claim(text="second claim")
    await repo.add(first)
    await repo.add(second)
    loaded = await repo.get(first.id)
    assert loaded is not None
    assert loaded.language is Language.YORUBA
    assert loaded.submitted_via is ChannelKind.TELEGRAM
    recent = await repo.list_recent(limit=10)
    assert [c.id for c in recent] == [second.id, first.id]
    assert len(await repo.list_recent(limit=1)) == 1
    assert await repo.get(Claim(text="never stored").id) is None
