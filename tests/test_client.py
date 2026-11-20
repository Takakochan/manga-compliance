import json
from pathlib import Path

import httpx
import pytest

from manga_compliance.client import ApiError, FukidashiClient

RESULT = {
    "status": "ok",
    "summary": "A fight.",
    "flags": [
        {
            "bbox": [1, 2, 3, 4],
            "source": "image",
            "category": "violence",
            "severity": "strong",
            "confidence": 0.95,
            "evidence": "blood",
        }
    ],
    "size": [10, 10],
    "seconds": 1.2,
    "error": None,
}


def server(request: httpx.Request) -> httpx.Response:
    if request.headers.get("X-API-Key") != "k" * 20:
        return httpx.Response(401, json={"detail": "missing or wrong X-API-Key"})
    if request.url.path == "/health":
        return httpx.Response(200, json={"status": "ok"})
    return httpx.Response(200, content=json.dumps(RESULT))


def client(key: str = "k" * 20) -> FukidashiClient:
    return FukidashiClient("https://api.test/", key, transport=httpx.MockTransport(server))


@pytest.fixture
def page(tmp_path: Path) -> Path:
    path = tmp_path / "page.png"
    path.write_bytes(b"png")
    return path


async def test_flags_parses_the_answer(page: Path) -> None:
    async with client() as c:
        result = await c.flags(page)
    assert result.flags[0].category == "violence"


async def test_wrong_key_raises_with_the_server_message(page: Path) -> None:
    async with client(key="wrong") as c:
        with pytest.raises(ApiError, match="401"):
            await c.flags(page)


async def test_health() -> None:
    async with client() as c:
        assert await c.health()


def test_missing_settings_explain_what_to_set() -> None:
    with pytest.raises(ApiError, match="FUKIDASHI_API_URL"):
        FukidashiClient("", "")
