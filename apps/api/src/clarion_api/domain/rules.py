"""Publishing rules. These protect real people from unreviewed messages.

Every broadcast path must call ensure_publishable. Tests in
tests/unit/test_rules.py pin each rule; do not weaken them without an ADR.
"""

from collections.abc import Iterable

from clarion_api.domain.enums import Language, ReviewStatus, Verdict
from clarion_api.domain.errors import NotPublishableError
from clarion_api.domain.models import MasterMessage


def ensure_publishable(message: MasterMessage, languages: Iterable[Language]) -> None:
    if message.review is None or message.review.status is not ReviewStatus.APPROVED:
        raise NotPublishableError("message has no approved review")

    if message.verdict in {Verdict.CONFIRMED, Verdict.CONTRADICTED} and message.passage is None:
        raise NotPublishableError(f"verdict '{message.verdict}' must cite an official passage")

    approved = {loc.language for loc in message.localisations if loc.is_approved}
    missing = [lang for lang in languages if lang is not Language.ENGLISH and lang not in approved]
    if missing:
        codes = ", ".join(sorted(lang.value for lang in missing))
        raise NotPublishableError(f"translations not approved for: {codes}")

    if message.integrity_hash is None:
        raise NotPublishableError("message has no integrity hash; seal it after approval")
