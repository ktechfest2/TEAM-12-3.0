from datetime import UTC, datetime

from fastapi import APIRouter, Request, status

from clarion_api.adapters.crypto import Cipher
from clarion_api.api.container import Container
from clarion_api.api.deps import ContainerDep
from clarion_api.api.schemas import (
    CodeSentOut,
    ConfirmIn,
    SmsPreferencesIn,
    SubscribeIn,
    SubscriptionConfirmedOut,
    UnsubscribeIn,
)
from clarion_api.domain.errors import FeatureUnavailableError
from clarion_api.domain.models import SmsPreferences
from clarion_api.services import sms_subscriptions as service

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


def _cipher(container: Container) -> Cipher:
    if container.cipher is None:
        msg = "Phone subscriptions are not switched on for this deployment."
        raise FeatureUnavailableError(msg)
    return container.cipher


def _throttle(container: Container, request: Request, now: datetime) -> None:
    """Per client address and overall, so the code endpoints cannot drain SMS credit."""
    client = request.headers.get("cf-connecting-ip") or (
        request.client.host if request.client else "unknown"
    )
    container.code_limiter_per_client.hit(client, now)
    container.code_limiter_overall.hit("all", now)


@router.post("", status_code=status.HTTP_202_ACCEPTED, operation_id="startSubscription")
async def start_subscription(
    body: SubscribeIn, request: Request, container: ContainerDep
) -> CodeSentOut:
    """Text a 6 digit code to the number. Nothing is active until it is confirmed."""
    cipher = _cipher(container)
    now = datetime.now(UTC)
    _throttle(container, request, now)
    await service.request_signup(
        raw_phone=body.phone,
        preferences=SmsPreferences(**body.model_dump(exclude={"phone"})),
        secret=container.settings.auth_jwt_secret.get_secret_value(),
        cipher=cipher,
        sender=container.sms_sender,
        repo=container.sms_subscriptions,
        now=now,
    )
    return CodeSentOut()


@router.post("/confirm", operation_id="confirmSubscription")
async def confirm_subscription(
    body: ConfirmIn, container: ContainerDep
) -> SubscriptionConfirmedOut:
    """Confirm a code for a signup, a preference change or a removal."""
    result = await service.confirm_code(
        raw_phone=body.phone,
        code=body.code,
        secret=container.settings.auth_jwt_secret.get_secret_value(),
        repo=container.sms_subscriptions,
        now=datetime.now(UTC),
    )
    if result.removed or result.preferences is None:
        return SubscriptionConfirmedOut(status="removed")
    return SubscriptionConfirmedOut(
        status="active", preferences=SmsPreferencesIn(**result.preferences.model_dump())
    )


@router.post("/unsubscribe", status_code=status.HTTP_202_ACCEPTED, operation_id="startUnsubscribe")
async def start_unsubscribe(
    body: UnsubscribeIn, request: Request, container: ContainerDep
) -> CodeSentOut:
    """Text a code to confirm removal, then confirm it with the confirm endpoint."""
    _cipher(container)
    now = datetime.now(UTC)
    _throttle(container, request, now)
    await service.request_unsubscribe(
        raw_phone=body.phone,
        secret=container.settings.auth_jwt_secret.get_secret_value(),
        sender=container.sms_sender,
        repo=container.sms_subscriptions,
        now=now,
    )
    return CodeSentOut()
