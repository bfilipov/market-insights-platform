"""HTTP Client for CoinCap API."""

import logging
from typing import Any, Dict

import httpx

from market_data.clients.base import ResilientHttpClient
from market_data.config import get_settings
from market_data.exceptions import AssetNotFoundException, ExternalApiUnavailableException

logger = logging.getLogger(__name__)


class CoinCapClient(ResilientHttpClient):
    """Client for CoinCap API."""

    def __init__(self):
        settings = get_settings()

        headers = {
            "authorization": f"Bearer {settings.coincap_api_key}",
            "Accept": "application/json",
        }

        super().__init__(
            base_url=settings.coincap_base_url,
            timeout=settings.market_data_request_timeout,
            max_retries=settings.market_data_max_retries,
            default_headers=headers
        )

    async def get_asset_data(self, asset_id: str) -> Dict[str, Any]:
        try:
            return await self._get(f"/assets/{asset_id}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise AssetNotFoundException(asset_id)
            raise ExternalApiUnavailableException("coincap")
        except (httpx.ConnectError, httpx.TimeoutException):
            raise ExternalApiUnavailableException("coincap")
