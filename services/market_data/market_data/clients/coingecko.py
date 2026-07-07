"""HTTP Client for CoinGecko API."""

import logging
from typing import Any, Dict

import httpx

from market_data.clients.base import ResilientHttpClient
from market_data.config import get_settings
from market_data.exceptions import AssetNotFoundException, ExternalApiUnavailableException

logger = logging.getLogger(__name__)


class CoinGeckoClient(ResilientHttpClient):
    """Client for CoinGecko API."""

    def __init__(self):
        settings = get_settings()
        super().__init__(
            base_url=settings.coingecko_base_url,
            timeout=settings.market_data_request_timeout,
        )

    async def get_coin_data(self, coin_id: str) -> Dict[str, Any]:
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false",
            "sparkline": "false",
        }
        try:
            return await self._get(f"/coins/{coin_id}", params=params)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise AssetNotFoundException(coin_id)
            raise ExternalApiUnavailableException("coingecko")
        except (httpx.ConnectError, httpx.TimeoutException):
            raise ExternalApiUnavailableException("coingecko")
