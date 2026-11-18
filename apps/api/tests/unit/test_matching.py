from clarion_api.adapters.llm.fake import FakeLanguageModel
from clarion_api.domain.enums import Verdict
from clarion_api.domain.models import Claim, SourcePassage
from clarion_api.repositories.memory import MemorySourceRepository
from clarion_api.services.matching import match_claim


async def _repo(llm: FakeLanguageModel, *texts: str) -> MemorySourceRepository:
    repo = MemorySourceRepository()
    for text in texts:
        p = SourcePassage(
            document_title="t", publisher="INEC", url="https://example.org", text=text
        )
        [vec] = await llm.embed([text])
        await repo.add(p, vec)
    return repo


async def test_contradicted_claim_cites_a_passage() -> None:
    llm = FakeLanguageModel()
    repo = await _repo(llm, "INEC said the campaign timetable graphic is fake and was not issued.")
    result = await match_claim(
        Claim(text="INEC issued a new campaign timetable"), llm=llm, sources=repo
    )
    assert result.verdict is Verdict.CONTRADICTED
    assert result.passage_id is not None


async def test_unrelated_claim_has_no_official_statement() -> None:
    llm = FakeLanguageModel()
    repo = await _repo(llm, "PVC distribution resumes in December.")
    result = await match_claim(
        Claim(text="A famous musician endorsed a party"), llm=llm, sources=repo
    )
    assert result.verdict is Verdict.NO_OFFICIAL_STATEMENT
    assert result.passage_id is None


async def test_empty_registry_has_no_official_statement() -> None:
    result = await match_claim(
        Claim(text="anything"), llm=FakeLanguageModel(), sources=MemorySourceRepository()
    )
    assert result.verdict is Verdict.NO_OFFICIAL_STATEMENT
