from typing import Annotated

from fastapi import Depends, Header, Request

from clarion_api.api.container import Container
from clarion_api.domain.errors import NotAuthorizedError
from clarion_api.domain.models import utc_now
from clarion_api.services.tokens import verify_token


def get_container(request: Request) -> Container:
    container: Container = request.app.state.container
    return container


ContainerDep = Annotated[Container, Depends(get_container)]


def get_reviewer(
    container: ContainerDep, authorization: Annotated[str | None, Header()] = None
) -> str:
    """The reviewer's name from a valid bearer token. Anything else is a 401."""
    scheme, _, token = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not token:
        msg = "a reviewer token is required (Authorization: Bearer <token>)"
        raise NotAuthorizedError(msg)
    secret = container.settings.auth_jwt_secret.get_secret_value()
    return verify_token(secret, token.strip(), now=utc_now())


ReviewerDep = Annotated[str, Depends(get_reviewer)]
