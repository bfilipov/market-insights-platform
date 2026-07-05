import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from api_gateway.config import get_settings

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseServiceClient(ABC, Generic[T]):
    """
    Abstract base class for service clients.

    Implements the Template Method pattern, defining the skeleton
    of the HTTP request flow while allowing subclasses to specify
    specific details like endpoints and response parsing.
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "BaseServiceClient":
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    async def _ensure_client(self) -> None:
        """Lazily initialize the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0),
                headers=self._get_default_headers(),
            )

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    @abstractmethod
    def _get_base_url(self) -> str:
        """Return the base URL for this service."""
        ...

    @abstractmethod
    def _get_api_key(self) -> str:
        """Return the API key for this service."""
        ...

    def _get_default_headers(self) -> Dict[str, str]:
        """Return default headers for all requests."""
        return {
            "Authorization": f"Bearer {self._get_api_key()}",
            "Content-Type": "application/json",
            "X-Service-Name": "api-gateway",
        }

    @retry(
        retry=retry_if_exception_type(httpx.ConnectError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=1, max=10),
        reraise=True,
    )
    async def _get(self, path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        Execute a GET request with retry logic.

        Args:
            path: The API path (appended to base URL)
            params: Optional query parameters

        Returns:
            The JSON response as a dictionary

        Raises:
            httpx.HTTPError: If the request fails after retries
        """
        await self._ensure_client()
        url = f"{self._get_base_url()}{path}"

        logger.debug(f"Making GET request to {url}")

        response = await self._client.get(url, params=params)  # type: ignore
        response.raise_for_status()

        return response.json()

    @abstractmethod
    async def fetch(self, **kwargs) -> T:
        """
        Fetch data from the service.

        Each client must implement this with its specific logic.

        Returns:
            Parsed and typed response data
        """
        ...
