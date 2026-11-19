import hashlib

import httpx

CLAIM = "INEC has released a new 2027 campaign timetable graphic"


async def _sealed_message(client: httpx.AsyncClient) -> str:
    claim = (await client.post("/claims", json={"text": CLAIM})).json()
    message = (await client.post("/messages", json={"claim_id": claim["id"]})).json()
    message_id: str = message["id"]
    await client.put(f"/messages/{message_id}/localisations", json={"language": "yo"})
    await client.post(f"/messages/{message_id}/localisations/yo/approval")
    await client.post(f"/messages/{message_id}/reviews", json={"status": "approved"})
    sealed = await client.post(f"/messages/{message_id}/seal")
    assert sealed.status_code == 200
    return message_id


async def test_sealed_correction_is_public_without_signing_in(
    client: httpx.AsyncClient, anonymous_client: httpx.AsyncClient
) -> None:
    message_id = await _sealed_message(client)
    response = await anonymous_client.get(f"/public/corrections/{message_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["claim_text"] == CLAIM
    assert body["verdict"] == "contradicted"
    assert body["source"]["url"].startswith("https://")
    assert body["approved_by"] == "reviewer-1"
    assert body["approved_at"]
    assert body["sealed_at"]
    assert body["integrity_hash"].startswith("sha256:")
    assert body["integrity_verified"] is True
    assert [t["language"] for t in body["translations"]] == ["yo"]


async def test_anyone_can_recompute_the_hash_from_the_published_record(
    client: httpx.AsyncClient, anonymous_client: httpx.AsyncClient
) -> None:
    message_id = await _sealed_message(client)
    body = (await anonymous_client.get(f"/public/corrections/{message_id}")).json()
    digest = hashlib.sha256(body["canonical_json"].encode("utf-8")).hexdigest()
    assert body["integrity_hash"] == f"sha256:{digest}"


async def test_the_record_exposes_no_internal_or_personal_fields(
    client: httpx.AsyncClient, anonymous_client: httpx.AsyncClient
) -> None:
    message_id = await _sealed_message(client)
    body = (await anonymous_client.get(f"/public/corrections/{message_id}")).json()
    assert set(body) == {
        "message_id",
        "claim_text",
        "verdict",
        "summary",
        "source",
        "translations",
        "approved_by",
        "approved_at",
        "sealed_at",
        "integrity_hash",
        "previous_hash",
        "hash_algorithm",
        "canonical_json",
        "integrity_verified",
    }


async def test_the_second_correction_links_to_the_first_hash(
    client: httpx.AsyncClient, anonymous_client: httpx.AsyncClient
) -> None:
    first_id = await _sealed_message(client)
    second_id = await _sealed_message(client)
    first = (await anonymous_client.get(f"/public/corrections/{first_id}")).json()
    second = (await anonymous_client.get(f"/public/corrections/{second_id}")).json()
    assert first["previous_hash"] is None
    assert second["previous_hash"] == first["integrity_hash"]
    assert second["integrity_verified"] is True


async def test_anyone_can_hear_an_approved_language_and_it_is_made_once(
    client: httpx.AsyncClient, anonymous_client: httpx.AsyncClient
) -> None:
    message_id = await _sealed_message(client)
    for language in ("yo", "en"):
        response = await anonymous_client.get(
            f"/public/corrections/{message_id}/voice/{language}", follow_redirects=False
        )
        assert response.status_code == 302
        assert response.headers["location"].endswith(
            f"/media/renditions/{message_id}/voice-{language}.ogg"
        )
    again = await anonymous_client.get(
        f"/public/corrections/{message_id}/voice/yo", follow_redirects=False
    )
    assert again.status_code == 302


async def test_a_language_without_approved_text_has_no_audio(
    client: httpx.AsyncClient, anonymous_client: httpx.AsyncClient
) -> None:
    message_id = await _sealed_message(client)
    response = await anonymous_client.get(f"/public/corrections/{message_id}/voice/ha")
    assert response.status_code == 404


async def test_a_draft_has_no_public_audio(
    client: httpx.AsyncClient, anonymous_client: httpx.AsyncClient
) -> None:
    claim = (await client.post("/claims", json={"text": CLAIM})).json()
    message = (await client.post("/messages", json={"claim_id": claim["id"]})).json()
    response = await anonymous_client.get(f"/public/corrections/{message['id']}/voice/en")
    assert response.status_code == 404


async def test_a_draft_is_not_public(
    client: httpx.AsyncClient, anonymous_client: httpx.AsyncClient
) -> None:
    claim = (await client.post("/claims", json={"text": CLAIM})).json()
    message = (await client.post("/messages", json={"claim_id": claim["id"]})).json()
    response = await anonymous_client.get(f"/public/corrections/{message['id']}")
    assert response.status_code == 404


async def test_a_correction_edited_after_sealing_stops_being_public(
    client: httpx.AsyncClient, anonymous_client: httpx.AsyncClient
) -> None:
    message_id = await _sealed_message(client)
    await client.post(
        f"/messages/{message_id}/reviews", json={"status": "approved", "summary": "New wording."}
    )
    response = await anonymous_client.get(f"/public/corrections/{message_id}")
    assert response.status_code == 404


async def test_an_unknown_id_is_a_404(anonymous_client: httpx.AsyncClient) -> None:
    missing = "00000000-0000-0000-0000-000000000000"
    assert (await anonymous_client.get(f"/public/corrections/{missing}")).status_code == 404
