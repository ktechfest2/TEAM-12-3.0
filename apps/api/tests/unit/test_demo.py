from importlib.resources import files

import pytest

from clarion_api.adapters.llm.fake import FakeLanguageModel
from clarion_api.config import AppEnv, Settings
from clarion_api.domain.enums import ChannelKind, Language, Verdict
from clarion_api.repositories.memory import (
    MemoryClaimRepository,
    MemoryMessageRepository,
    MemorySourceRepository,
)
from clarion_api.services.demo import (
    LIVE_CLAIM,
    QUEUED_CLAIMS,
    ResetNotAllowedError,
    ensure_reset_allowed,
    queue_demo_claims,
)
from clarion_api.services.intake import submit_claim
from clarion_api.services.sources import load_passages, parse_passages


async def _seeded() -> tuple[MemorySourceRepository, FakeLanguageModel]:
    sources = MemorySourceRepository()
    llm = FakeLanguageModel()
    raw = files("clarion_api.data").joinpath("seed_sources.json").read_text(encoding="utf-8")
    await load_passages(parse_passages(raw), sources=sources, llm=llm)
    return sources, llm


async def test_each_demo_claim_gets_the_verdict_the_script_promises() -> None:
    sources, llm = await _seeded()
    for demo in (*QUEUED_CLAIMS, LIVE_CLAIM):
        _, result = await submit_claim(
            demo.text,
            language=Language.ENGLISH,
            via=ChannelKind.WEB_FEED,
            claims=MemoryClaimRepository(),
            sources=sources,
            llm=llm,
        )
        assert result.verdict is demo.expected_verdict, demo.text


def test_the_demo_covers_all_three_verdicts() -> None:
    verdicts = {d.expected_verdict for d in (*QUEUED_CLAIMS, LIVE_CLAIM)}
    assert verdicts == set(Verdict)


async def test_queued_claims_become_drafts_for_the_reviewer() -> None:
    sources, llm = await _seeded()
    claims, messages = MemoryClaimRepository(), MemoryMessageRepository()
    drafts = await queue_demo_claims(claims=claims, sources=sources, messages=messages, llm=llm)
    assert [d.verdict for d in drafts] == [c.expected_verdict for c in QUEUED_CLAIMS]
    assert all(d.review is None and d.integrity_hash is None for d in drafts)
    assert len(await messages.list_recent(limit=10)) == len(QUEUED_CLAIMS)


def _settings(**overrides: object) -> Settings:
    base: dict[str, object] = {"app_env": AppEnv.DEVELOPMENT, "repository_backend": "sql"}
    return Settings(**{**base, **overrides}, _env_file=None)  # type: ignore[arg-type]


def test_reset_is_allowed_in_development_with_sql_and_confirmation() -> None:
    ensure_reset_allowed(_settings(), confirmed=True)


def test_reset_is_refused_in_production() -> None:
    from pydantic import SecretStr  # noqa: PLC0415

    production = _settings(app_env=AppEnv.PRODUCTION, auth_jwt_secret=SecretStr("a-real-secret"))
    with pytest.raises(ResetNotAllowedError, match="production"):
        ensure_reset_allowed(production, confirmed=True)


def test_reset_is_refused_without_the_sql_backend() -> None:
    with pytest.raises(ResetNotAllowedError, match="REPOSITORY_BACKEND=sql"):
        ensure_reset_allowed(_settings(repository_backend="memory"), confirmed=True)


def test_reset_is_refused_without_confirmation() -> None:
    with pytest.raises(ResetNotAllowedError, match="--yes"):
        ensure_reset_allowed(_settings(), confirmed=False)
