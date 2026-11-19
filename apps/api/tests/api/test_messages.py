import httpx

from clarion_api.adapters.channels.console import ConsoleChannel

CLAIM = "INEC has released a new 2027 campaign timetable graphic"


async def _message(client: httpx.AsyncClient) -> dict[str, object]:
    claim = (await client.post("/claims", json={"text": CLAIM})).json()
    response = await client.post("/messages", json={"claim_id": claim["id"]})
    assert response.status_code == 201
    body: dict[str, object] = response.json()
    return body


async def _approve(client: httpx.AsyncClient, message_id: object) -> None:
    review = {"status": "approved"}
    assert (await client.post(f"/messages/{message_id}/reviews", json=review)).status_code == 201


async def _approve_yoruba(client: httpx.AsyncClient, message_id: object) -> None:
    drafted = await client.put(f"/messages/{message_id}/localisations", json={"language": "yo"})
    assert drafted.json()["localisations"][0]["is_approved"] is False
    approved = await client.post(f"/messages/{message_id}/localisations/yo/approval")
    assert approved.json()["localisations"][0]["is_approved"] is True


async def test_message_is_drafted_from_claim_with_a_cited_source(client: httpx.AsyncClient) -> None:
    message = await _message(client)
    assert message["verdict"] == "contradicted"
    assert message["claim_text"] == CLAIM
    assert message["source"] is not None
    assert message["review"] is None
    assert message["integrity_hash"] is None


async def test_message_for_unknown_claim_is_404(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/messages", json={"claim_id": "00000000-0000-0000-0000-000000000000"}
    )
    assert response.status_code == 404


async def test_unapproved_message_returns_409_and_sends_nothing(
    client: httpx.AsyncClient, console: ConsoleChannel
) -> None:
    message = await _message(client)
    response = await client.post(f"/messages/{message['id']}/broadcast", json={})
    assert response.status_code == 409
    assert console.sent == []
    assert (await client.get(f"/messages/{message['id']}/deliveries")).json() == []


async def test_approved_but_unsealed_message_is_not_broadcast(
    client: httpx.AsyncClient, console: ConsoleChannel
) -> None:
    message = await _message(client)
    await _approve(client, message["id"])
    response = await client.post(f"/messages/{message['id']}/broadcast", json={})
    assert response.status_code == 409
    assert console.sent == []


async def test_rejected_message_cannot_be_sealed(client: httpx.AsyncClient) -> None:
    message = await _message(client)
    review = {"status": "rejected", "note": "weak match"}
    await client.post(f"/messages/{message['id']}/reviews", json=review)
    assert (await client.post(f"/messages/{message['id']}/seal")).status_code == 409


async def test_full_flow_broadcasts_each_language_and_records_receipts(
    client: httpx.AsyncClient, console: ConsoleChannel
) -> None:
    message = await _message(client)
    await _approve(client, message["id"])
    await _approve_yoruba(client, message["id"])
    sealed = await client.post(f"/messages/{message['id']}/seal")
    assert sealed.json()["integrity_hash"].startswith("sha256:")

    response = await client.post(f"/messages/{message['id']}/broadcast", json={})
    assert response.status_code == 202
    deliveries = response.json()
    assert {d["language"] for d in deliveries} == {"en", "yo"}
    assert all(d["status"] == "sent" and d["sent_at"] for d in deliveries)
    assert len(console.sent) == 2
    assert any("[yo]" in text for text in console.sent)


async def test_unapproved_translation_blocks_broadcast_of_that_language(
    client: httpx.AsyncClient, console: ConsoleChannel
) -> None:
    message = await _message(client)
    await _approve(client, message["id"])
    await client.put(f"/messages/{message['id']}/localisations", json={"language": "ha"})
    await client.post(f"/messages/{message['id']}/seal")
    response = await client.post(
        f"/messages/{message['id']}/broadcast", json={"languages": ["en", "ha"]}
    )
    assert response.status_code == 409
    assert "ha" in response.json()["detail"]
    assert console.sent == []


async def test_editing_the_summary_after_approval_voids_the_seal(
    client: httpx.AsyncClient, console: ConsoleChannel
) -> None:
    message = await _message(client)
    await _approve(client, message["id"])
    await client.post(f"/messages/{message['id']}/seal")
    edited = await client.post(
        f"/messages/{message['id']}/reviews",
        json={"status": "approved", "summary": "A clearer summary."},
    )
    assert edited.json()["integrity_hash"] is None
    assert (await client.post(f"/messages/{message['id']}/broadcast", json={})).status_code == 409
    assert console.sent == []


async def test_seals_are_chained_to_the_previous_message(client: httpx.AsyncClient) -> None:
    first = await _message(client)
    await _approve(client, first["id"])
    first_sealed = (await client.post(f"/messages/{first['id']}/seal")).json()
    second = await _message(client)
    await _approve(client, second["id"])
    second_sealed = (await client.post(f"/messages/{second['id']}/seal")).json()
    assert first_sealed["integrity_hash"] != second_sealed["integrity_hash"]


async def test_retraction_notifies_the_channel_and_marks_deliveries(
    client: httpx.AsyncClient, console: ConsoleChannel
) -> None:
    message = await _message(client)
    await _approve(client, message["id"])
    await client.post(f"/messages/{message['id']}/seal")
    await client.post(f"/messages/{message['id']}/broadcast", json={})
    assert len(console.sent) == 1

    response = await client.post(
        f"/messages/{message['id']}/retraction",
        json={"reason": "The source was updated."},
    )
    assert response.status_code == 200
    assert [d["status"] for d in response.json()] == ["retracted"]
    assert len(console.sent) == 2
    assert "withdrawn" in console.sent[1]
    assert "The source was updated." in console.sent[1]


async def test_unknown_message_is_404(client: httpx.AsyncClient) -> None:
    missing = "00000000-0000-0000-0000-000000000000"
    assert (await client.get(f"/messages/{missing}")).status_code == 404
    assert (await client.post(f"/messages/{missing}/seal")).status_code == 404


async def test_english_needs_no_localisation(client: httpx.AsyncClient) -> None:
    message = await _message(client)
    response = await client.put(f"/messages/{message['id']}/localisations", json={"language": "en"})
    assert response.status_code == 409
