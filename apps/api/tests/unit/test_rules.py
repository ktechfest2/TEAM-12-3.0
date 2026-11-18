import pytest

from clarion_api.domain.enums import Language, ReviewStatus, Verdict
from clarion_api.domain.errors import NotPublishableError
from clarion_api.domain.models import Review
from clarion_api.domain.rules import ensure_publishable
from tests.factories import approved_message

LANGS = [Language.ENGLISH, Language.YORUBA]


def test_approved_sealed_message_is_publishable() -> None:
    ensure_publishable(approved_message(), LANGS)


def test_unreviewed_message_is_blocked() -> None:
    with pytest.raises(NotPublishableError, match="approved review"):
        ensure_publishable(approved_message(review=None), LANGS)


def test_rejected_review_is_blocked() -> None:
    msg = approved_message()
    rejected = Review(claim_id=msg.claim_id, reviewer_id="r", status=ReviewStatus.REJECTED)
    with pytest.raises(NotPublishableError):
        ensure_publishable(msg.model_copy(update={"review": rejected}), LANGS)


@pytest.mark.parametrize("verdict", [Verdict.CONFIRMED, Verdict.CONTRADICTED])
def test_factual_verdict_without_citation_is_blocked(verdict: Verdict) -> None:
    with pytest.raises(NotPublishableError, match="cite"):
        ensure_publishable(approved_message(verdict=verdict, passage=None), LANGS)


def test_unapproved_translation_is_blocked() -> None:
    with pytest.raises(NotPublishableError, match="ha"):
        ensure_publishable(approved_message(), [Language.HAUSA])


def test_unsealed_message_is_blocked() -> None:
    with pytest.raises(NotPublishableError, match="hash"):
        ensure_publishable(approved_message(integrity_hash=None), LANGS)
