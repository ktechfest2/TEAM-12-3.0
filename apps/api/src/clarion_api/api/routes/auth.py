from datetime import timedelta

from fastapi import APIRouter, status

from clarion_api.api.deps import ContainerDep
from clarion_api.api.schemas import TokenIn, TokenOut
from clarion_api.domain.errors import NotAuthorizedError
from clarion_api.domain.models import utc_now
from clarion_api.services.tokens import invite_code_matches, issue_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/tokens", status_code=status.HTTP_201_CREATED, operation_id="createToken")
async def create_token(body: TokenIn, container: ContainerDep) -> TokenOut:
    """Exchange an invite code for a signed reviewer token."""
    settings = container.settings
    invite = settings.auth_reviewer_invite_code
    if not invite_code_matches(invite.get_secret_value() if invite else None, body.invite_code):
        msg = "invite code is not valid"
        raise NotAuthorizedError(msg)
    ttl = timedelta(minutes=settings.auth_token_ttl_minutes)
    token = issue_token(
        settings.auth_jwt_secret.get_secret_value(), body.reviewer_name, now=utc_now(), ttl=ttl
    )
    return TokenOut(
        access_token=token,
        expires_in_seconds=int(ttl.total_seconds()),
        reviewer_name=body.reviewer_name,
    )
