"""
Client for the Market Data Service.
"""

import logging

import httpx

from api_gateway.clients.base import BaseServiceClient
from api_gateway.exceptions import (
    AssetNotFoundException,
    ExternalServiceException,
    ServiceUnavailableException,
)
from api_gateway.models.responses import MarketDataResponse

logger = logging.getLogger(__name__)


class MarketDataClient(BaseServiceClient[MarketDataResponse]):
    """
    HTTP client for the Market Data Service.
    """

    def _get_base_url(self) -> str:
        return self._settings.market_data_service_url

    def _get_api_key(self) -> str:
        return self._settings.market_data_internal_api_key

    async def fetch_market_data(self, symbol: str) -> MarketDataResponse:
        """
        Fetch market data for a given symbol.

        Args:
            symbol: The asset symbol (e.g., 'bitcoin', 'ethereum')

        Returns:
            Normalized market data response

        Raises:
            AssetNotFoundException: If the symbol is not found
            ServiceUnavailableException: If the service is down
            ExternalServiceException: For other service errors
        """
        try:
            data = await self._get(f"/api/v1/market/{symbol}")
            return MarketDataResponse(**data)

        except httpx.HTTPStatusError as e:
            logger.error(f"Market Data Service error: {e.response.status_code}")

            if e.response.status_code == 404:

                raise AssetNotFoundException(symbol)
            elif e.response.status_code == 503:
                raise ServiceUnavailableException("market-data")
            else:
                raise ExternalServiceException(
                    "market-data",
                    f"HTTP {e.response.status_code}: {e.response.text}",
                )

        except httpx.ConnectError:
            logger.error("Cannot connect to Market Data Service")
            raise ServiceUnavailableException("market-data")

        except httpx.TimeoutException:
            logger.error("Market Data Service request timed out")
            raise ServiceUnavailableException("market-data")

        except Exception as e:
            logger.exception(f"Unexpected error calling Market Data Service: {e}")
            raise ExternalServiceException("market-data", str(e))

    async def fetch(self, symbol: str) -> MarketDataResponse:
        """Implementation of the abstract fetch method."""
        return await self.fetch_market_data(symbol)
