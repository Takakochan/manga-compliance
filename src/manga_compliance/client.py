import mimetypes
from pathlib import Path

import httpx

from manga_compliance.models import FlagsResult
from manga_compliance.settings import settings


class ApiError(RuntimeError):
    pass


class FukidashiClient:
    def __init__(
        self,
        url: str = settings.fukidashi_api_url,
        key: str = settings.fukidashi_api_key,
        timeout: float = settings.request_timeout,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if not url or not key:
            raise ApiError("set FUKIDASHI_API_URL and FUKIDASHI_API_KEY in .env")
        self._http = httpx.AsyncClient(
            base_url=url.rstrip("/"),
            headers={"X-API-Key": key},
            timeout=timeout,
            transport=transport,
        )

    async def __aenter__(self) -> "FukidashiClient":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self._http.aclose()

    async def health(self) -> bool:
        response = await self._http.get("/health")
        return response.status_code == 200

    async def flags(self, image: Path) -> FlagsResult:
        mime = mimetypes.guess_type(image.name)[0] or "image/png"
        files = {"image": (image.name, image.read_bytes(), mime)}
        response = await self._http.post("/flags", files=files)
        if response.status_code != 200:
            raise ApiError(
                f"{response.status_code}: {response.json().get('detail', response.text)}"
            )
        return FlagsResult.model_validate(response.json())
