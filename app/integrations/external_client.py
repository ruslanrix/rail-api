from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class ExternalClientConfig:
    base_url: str
    timeout_s: float = 3.0


class ExternalUpstreamError(Exception):
    """Any upstream / external service error we want to map to 502."""


class ExternalClient:
    def __init__(self, cfg: ExternalClientConfig, client: httpx.AsyncClient | None = None) -> None:
        self._cfg = cfg
        self._client = client

    def _build_client(self) -> httpx.AsyncClient:
        # We build a short-lived client only if DI didn't provide one.
        return httpx.AsyncClient(
            base_url=self._cfg.base_url,
            timeout=httpx.Timeout(self._cfg.timeout_s),
        )

    async def ping(self) -> dict[str, Any]:
        """
        Calls GET /ping on external service.
        Expects JSON response.
        """
        if not self._cfg.base_url:
            raise ExternalUpstreamError("External base_url is not configured")

        if self._client is not None:
            return await self._ping_with(self._client)

        async with self._build_client() as client:
            return await self._ping_with(client)

    async def _ping_with(self, client: httpx.AsyncClient) -> dict[str, Any]:
        try:
            r = await client.get("/ping")
        except httpx.TimeoutException as e:
            raise ExternalUpstreamError("External request timed out") from e
        except httpx.HTTPError as e:
            raise ExternalUpstreamError("External request failed") from e

        if r.status_code >= 500:
            raise ExternalUpstreamError(f"External service error: {r.status_code}")

        if r.status_code >= 400:
            # 4xx тоже считаем upstream-проблемой, чтобы наружу не “протекал” контракт
            raise ExternalUpstreamError(f"External request rejected: {r.status_code}")

        try:
            data = r.json()
        except (json.JSONDecodeError, ValueError) as e:
            raise ExternalUpstreamError("External returned non-JSON response") from e

        if not isinstance(data, dict):
            raise ExternalUpstreamError("External returned unexpected JSON shape")

        return data
