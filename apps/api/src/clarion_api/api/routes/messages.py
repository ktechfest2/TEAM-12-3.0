from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from clarion_api.api.container import Container
from clarion_api.api.deps import ContainerDep, ReviewerDep, get_reviewer
from clarion_api.api.mappers import delivery_out, message_out
from clarion_api.api.schemas import (
    BroadcastIn,
    DeliveryOut,
    LocalisationIn,
    MessageCreateIn,
    MessageOut,
    RetractIn,
    ReviewIn,
)
from clarion_api.domain.enums import Language
from clarion_api.domain.models import MasterMessage
from clarion_api.services import messages as workflow
from clarion_api.worker.tasks import send_delivery

# Every message route is for invited reviewers; the public page reads sealed messages elsewhere.
router = APIRouter(prefix="/messages", tags=["messages"], dependencies=[Depends(get_reviewer)])

LimitQuery = Annotated[int, Query(ge=1, le=200)]


async def _out(container: Container, message: MasterMessage) -> MessageOut:
    claim = await container.claims.get(message.claim_id)
    return message_out(message, claim)


@router.post("", status_code=status.HTTP_201_CREATED, operation_id="createMessage")
async def create_message(body: MessageCreateIn, container: ContainerDep) -> MessageOut:
    message = await workflow.create_message(
        body.claim_id,
        claims=container.claims,
        sources=container.sources,
        messages=container.messages,
        llm=container.llm,
    )
    return await _out(container, message)


@router.get("", operation_id="listMessages")
async def list_messages(container: ContainerDep, limit: LimitQuery = 50) -> list[MessageOut]:
    recent = await container.messages.list_recent(limit=limit)
    return [await _out(container, m) for m in recent]


@router.get("/{message_id}", operation_id="getMessage")
async def get_message(message_id: UUID, container: ContainerDep) -> MessageOut:
    message = await workflow.load_message(message_id, container.messages)
    return await _out(container, message)


@router.post("/{message_id}/reviews", status_code=status.HTTP_201_CREATED, operation_id="addReview")
async def add_review(
    message_id: UUID, body: ReviewIn, container: ContainerDep, reviewer: ReviewerDep
) -> MessageOut:
    message = await workflow.add_review(
        message_id,
        reviewer_id=reviewer,
        status=body.status,
        note=body.note,
        summary=body.summary,
        messages=container.messages,
    )
    return await _out(container, message)


@router.put("/{message_id}/localisations", operation_id="setLocalisation")
async def set_localisation(
    message_id: UUID, body: LocalisationIn, container: ContainerDep
) -> MessageOut:
    message = await workflow.set_localisation(
        message_id,
        language=body.language,
        text=body.text,
        messages=container.messages,
        llm=container.llm,
    )
    return await _out(container, message)


@router.post("/{message_id}/localisations/{language}/approval", operation_id="approveLocalisation")
async def approve_localisation(
    message_id: UUID, language: Language, container: ContainerDep, reviewer: ReviewerDep
) -> MessageOut:
    message = await workflow.approve_localisation(
        message_id, language=language, approved_by=reviewer, messages=container.messages
    )
    return await _out(container, message)


@router.post("/{message_id}/seal", operation_id="sealMessage")
async def seal_message(
    message_id: UUID, container: ContainerDep, reviewer: ReviewerDep
) -> MessageOut:
    sealed = await workflow.seal_message(
        message_id, actor=reviewer, messages=container.messages, audit=container.audit
    )
    return await _out(container, sealed)


@router.post(
    "/{message_id}/broadcast", status_code=status.HTTP_202_ACCEPTED, operation_id="broadcastMessage"
)
async def broadcast_message(
    message_id: UUID, body: BroadcastIn, container: ContainerDep
) -> list[DeliveryOut]:
    planned = await workflow.plan_broadcast(
        message_id,
        languages=body.languages,
        channels=container.channels,
        messages=container.messages,
        deliveries=container.deliveries,
    )
    for delivery in planned:
        await send_delivery.kiq(str(delivery.id))
    planned_ids = {d.id for d in planned}
    stored = await container.deliveries.list_for_message(message_id)
    return [delivery_out(d) for d in stored if d.id in planned_ids]


@router.get("/{message_id}/deliveries", operation_id="listDeliveries")
async def list_deliveries(message_id: UUID, container: ContainerDep) -> list[DeliveryOut]:
    await workflow.load_message(message_id, container.messages)
    return [delivery_out(d) for d in await container.deliveries.list_for_message(message_id)]


@router.post("/{message_id}/retraction", operation_id="retractMessage")
async def retract_message(
    message_id: UUID, body: RetractIn, container: ContainerDep
) -> list[DeliveryOut]:
    retracted = await workflow.retract_message(
        message_id,
        reason=body.reason,
        public_url=f"{container.settings.public_web_url}/c/{message_id}",
        channels=container.channels,
        messages=container.messages,
        deliveries=container.deliveries,
    )
    return [delivery_out(d) for d in retracted]
