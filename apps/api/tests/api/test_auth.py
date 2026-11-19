import httpx
import pytest

from tests.conftest import INVITE_CODE

PROTECTED = [
    ("POST", "/messages"),
    ("GET", "/messages"),
    ("GET", "/messages/00000000-0000-0000-0000-000000000000"),
    ("POST", "/messages/00000000-0000-0000-0000-000000000000/reviews"),
    ("PUT", "/messages/00000000-0000-0000-0000-000000000000/localisations"),
    ("POST", "/messages/00000000-0000-0000-0000-000000000000/localisations/yo/approval"),
    ("POST", "/messages/00000000-0000-0000-0000-000000000000/seal"),
    ("POST", "/messages/00000000-0000-0000-0000-000000000000/broadcast"),
    ("POST", "/messages/00000000-0000-0000-0000-000000000000/retraction"),
    ("GET", "/messages/00000000-0000-0000-0000-000000000000/deliveries"),
]


@pytest.mark.parametrize(("method", "path"), PROTECTED)
async def test_message_routes_refuse_a_request_without_a_token(
    anonymous_client: httpx.AsyncClient, method: str, path: str
) -> None:
    response = await anonymous_client.request(method, path)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize("header", ["Bearer not-a-token", "Basic abc", "Bearer ", "garbage"])
async def test_message_routes_refuse_an_invalid_token(
    anonymous_client: httpx.AsyncClient, header: str
) -> None:
    response = await anonymous_client.get("/messages", headers={"Authorization": header})
    assert response.status_code == 401


async def test_token_signed_with_another_secret_is_refused(
    anonymous_client: httpx.AsyncClient,
) -> None:
    from datetime import timedelta  # noqa: PLC0415

    from clarion_api.domain.models import utc_now  # noqa: PLC0415
    from clarion_api.services.tokens import issue_token  # noqa: PLC0415

    forged = issue_token("another-secret", "mallory", now=utc_now(), ttl=timedelta(hours=1))
    headers = {"Authorization": f"Bearer {forged}"}
    response = await anonymous_client.get("/messages", headers=headers)
    assert response.status_code == 401


async def test_valid_invite_code_returns_a_working_token(
    anonymous_client: httpx.AsyncClient,
) -> None:
    issued = await anonymous_client.post(
        "/auth/tokens", json={"invite_code": INVITE_CODE, "reviewer_name": "Ada"}
    )
    assert issued.status_code == 201
    body = issued.json()
    assert body["reviewer_name"] == "Ada"
    assert body["expires_in_seconds"] > 0
    listed = await anonymous_client.get(
        "/messages", headers={"Authorization": f"Bearer {body['access_token']}"}
    )
    assert listed.status_code == 200


async def test_wrong_invite_code_is_refused(anonymous_client: httpx.AsyncClient) -> None:
    response = await anonymous_client.post(
        "/auth/tokens", json={"invite_code": "wrong", "reviewer_name": "Ada"}
    )
    assert response.status_code == 401


async def test_the_reviewer_name_in_the_token_is_recorded_on_the_review(
    client: httpx.AsyncClient,
) -> None:
    claim = (await client.post("/claims", json={"text": "INEC released a timetable"})).json()
    message = (await client.post("/messages", json={"claim_id": claim["id"]})).json()
    reviewed = await client.post(f"/messages/{message['id']}/reviews", json={"status": "approved"})
    assert reviewed.json()["review"]["reviewer_id"] == "reviewer-1"


async def test_claims_stay_public(anonymous_client: httpx.AsyncClient) -> None:
    response = await anonymous_client.post("/claims", json={"text": "Is voting on Saturday?"})
    assert response.status_code == 201
