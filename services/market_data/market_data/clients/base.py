"""Base HTTP client with resilience patterns."""

import logging
from abc import ABC
from typing import Any, Dict, Optional

import httpx
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from market_data.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class ResilientHttpClient(ABC):
    """Abstract base class for resilient HTTP clients."""

    def __init__(
            self,
            base_url: str,
            timeout: float = 10.0,
            default_headers: Optional[Dict[str, Any]] = None
    ):
        self._base_url = base_url.rstrip("/")
        self._default_headers = default_headers or {}
        self._timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "ResilientHttpClient":
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def _ensure_client(self) -> None:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers=self._default_headers,
                timeout=httpx.Timeout(self._timeout),
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            )

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    @retry(
        retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout)),
        stop=stop_after_attempt(settings.market_data_max_retries),
        wait=wait_exponential(multiplier=0.5, min=1, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        await self._ensure_client()
        url = f"{self._base_url}{path}"
        response = await self._client.get(url, params=params)  # type: ignore
        response.raise_for_status()
        return response.json()
