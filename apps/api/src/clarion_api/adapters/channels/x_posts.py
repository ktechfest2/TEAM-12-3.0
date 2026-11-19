"""Posts to X through the v2 API with an OAuth 2.0 user access token (scope tweet.write).

The token is short lived unless it was issued with offline.access; refresh it before a demo.
"""

import httpx

from clarion_api.domain.enums import ChannelKind

API_URL = "https://api.x.com/2/tweets"


class XChannel:
    kind = ChannelKind.X

    def __init__(self, *, access_token: str, client: httpx.AsyncClient) -> None:
        self._access_token = access_token
        self._client = client

    async def send_text(self, text: str) -> str:
        response = await self._client.post(
            API_URL,
            json={"text": text},
            headers={"Authorization": f"Bearer {self._access_token}"},
            timeout=15.0,
        )
        if response.status_code >= 400:
            detail = _detail(response)
            msg = f"x error {response.status_code}: {detail}"
            raise RuntimeError(msg)
        return str(response.json()["data"]["id"])


def _detail(response: httpx.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return "unknown"
    return str(body.get("detail") or body.get("title") or "unknown")
