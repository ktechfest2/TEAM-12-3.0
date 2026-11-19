"""Domain models to public response shapes. The only place routes build output schemas."""

from clarion_api.api.schemas import (
    DeliveryOut,
    LocalisationOut,
    MessageOut,
    ReviewOut,
    SourceOut,
)
from clarion_api.domain.models import Delivery, MasterMessage, SourcePassage


def source_out(passage: SourcePassage) -> SourceOut:
    return SourceOut(
        id=passage.id,
        document_title=passage.document_title,
        publisher=passage.publisher,
        url=str(passage.url),
        text=passage.text,
    )


def message_out(message: MasterMessage) -> MessageOut:
    review = message.review
    return MessageOut(
        id=message.id,
        claim_id=message.claim_id,
        verdict=message.verdict,
        summary=message.summary,
        confidence=message.confidence,
        source=source_out(message.passage) if message.passage else None,
        review=ReviewOut(
            reviewer_id=review.reviewer_id,
            status=review.status,
            note=review.note,
            created_at=review.created_at,
        )
        if review
        else None,
        localisations=[
            LocalisationOut(
                language=loc.language,
                text=loc.text,
                approved_by=loc.approved_by,
                is_approved=loc.is_approved,
            )
            for loc in message.localisations
        ],
        integrity_hash=message.integrity_hash,
        created_at=message.created_at,
    )


def delivery_out(delivery: Delivery) -> DeliveryOut:
    return DeliveryOut(
        id=delivery.id,
        message_id=delivery.message_id,
        channel=delivery.channel,
        language=delivery.language,
        status=delivery.status,
        external_id=delivery.external_id,
        error=delivery.error,
        sent_at=delivery.sent_at,
        created_at=delivery.created_at,
    )
