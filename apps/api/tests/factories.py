"""Builders for domain objects in tests. Keep defaults valid and publishable."""

from uuid import uuid4

from clarion_api.domain.enums import Language, ReviewStatus, Verdict
from clarion_api.domain.models import Localisation, MasterMessage, Review, SourcePassage
from clarion_api.services.integrity import seal


def passage() -> SourcePassage:
    return SourcePassage(
        document_title="Test statement",
        publisher="INEC",
        url="https://example.org/statement",
        text="The commission did not issue the timetable.",
    )


def approved_message(**overrides: object) -> MasterMessage:
    claim_id = uuid4()
    message = MasterMessage(
        claim_id=claim_id,
        verdict=Verdict.CONTRADICTED,
        passage=passage(),
        summary="INEC did not issue this timetable.",
        review=Review(claim_id=claim_id, reviewer_id="reviewer-1", status=ReviewStatus.APPROVED),
        localisations=(
            Localisation(language=Language.YORUBA, text="yo text", approved_by="native-yo"),
        ),
    )
    message = message.model_copy(update=overrides)
    return seal(message) if "integrity_hash" not in overrides else message
