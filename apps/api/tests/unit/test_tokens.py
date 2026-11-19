from datetime import UTC, datetime, timedelta

import pytest

from clarion_api.config import AppEnv, Settings
from clarion_api.domain.errors import NotAuthorizedError
from clarion_api.services.tokens import invite_code_matches, issue_token, verify_token

NOW = datetime(2027, 1, 15, 12, 0, tzinfo=UTC)
SECRET = "unit-test-secret"  # noqa: S105


def test_token_round_trips_the_subject() -> None:
    token = issue_token(SECRET, "Ada", now=NOW, ttl=timedelta(hours=1))
    assert verify_token(SECRET, token, now=NOW + timedelta(minutes=59)) == "Ada"


def test_expired_token_is_refused() -> None:
    token = issue_token(SECRET, "Ada", now=NOW, ttl=timedelta(hours=1))
    with pytest.raises(NotAuthorizedError):
        verify_token(SECRET, token, now=NOW + timedelta(hours=1))


def test_tampered_payload_is_refused() -> None:
    header, _, signature = issue_token(SECRET, "Ada", now=NOW, ttl=timedelta(hours=1)).split(".")
    forged_claims = issue_token(SECRET, "Root", now=NOW, ttl=timedelta(hours=1)).split(".")[1]
    with pytest.raises(NotAuthorizedError):
        verify_token(SECRET, f"{header}.{forged_claims}.{signature}", now=NOW)


def test_wrong_secret_is_refused() -> None:
    token = issue_token(SECRET, "Ada", now=NOW, ttl=timedelta(hours=1))
    with pytest.raises(NotAuthorizedError):
        verify_token("other", token, now=NOW)


@pytest.mark.parametrize("token", ["", "a.b", "a.b.c", "....", "x" * 50])
def test_malformed_token_is_refused(token: str) -> None:
    with pytest.raises(NotAuthorizedError):
        verify_token(SECRET, token, now=NOW)


def test_invite_code_comparison() -> None:
    assert invite_code_matches("open-sesame", "open-sesame")
    assert not invite_code_matches("open-sesame", "open-sesamE")
    assert not invite_code_matches(None, "anything")
    assert not invite_code_matches("", "")


def test_production_refuses_the_placeholder_signing_secret() -> None:
    with pytest.raises(ValueError, match="AUTH_JWT_SECRET"):
        Settings(app_env=AppEnv.PRODUCTION, _env_file=None)  # type: ignore[call-arg]


def test_empty_environment_values_count_as_not_set(monkeypatch: pytest.MonkeyPatch) -> None:
    # Compose passes every optional setting, empty when the deployer left it blank.
    monkeypatch.setenv("CHANNEL_TELEGRAM_WEBHOOK_SECRET", "")
    monkeypatch.setenv("AUTH_REVIEWER_INVITE_CODE", "")
    monkeypatch.setenv("LLM_MODEL", "")
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.channel_telegram_webhook_secret is None
    assert settings.auth_reviewer_invite_code is None
    assert settings.llm_model is None
