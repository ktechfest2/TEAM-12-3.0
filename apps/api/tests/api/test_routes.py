import httpx


async def test_health(client: httpx.AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["env"] == "test"


async def test_fake_timetable_claim_is_contradicted_with_source(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/claims", json={"text": "INEC has released a new 2027 campaign timetable graphic"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["verdict"] == "contradicted"
    assert body["source"]["url"].startswith("https://")


async def test_claim_validation(client: httpx.AsyncClient) -> None:
    response = await client.post("/claims", json={"text": "x"})
    assert response.status_code == 422


async def test_sms_size_tool(client: httpx.AsyncClient) -> None:
    response = await client.post("/tools/sms-size", json={"text": "Ẹ kú àárọ̀"})
    assert response.json()["encoding"] == "ucs2"
