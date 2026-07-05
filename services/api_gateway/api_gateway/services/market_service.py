"""
Market service - orchestrates business logic for market-related operations.
"""

import logging

from api_gateway.clients.market_data_client import MarketDataClient

from api_gateway.models.responses import (
    MarketDataResponse,
)

logger = logging.getLogger(__name__)


class MarketService:
    """
    Service class that orchestrates market data retrieval/
    """

    def __init__(
            self,
            market_data_client: MarketDataClient,
    ):
        """
        Initialize the market service.

        Args:
            market_data_client: Client for the Market Data Service
        """
        self._market_data_client = market_data_client

    async def get_market_data(self, symbol: str) -> MarketDataResponse:
        """
        Get market data for a symbol.

        Args:
            symbol: The asset symbol

        Returns:
            Normalized market data
        """
        logger.info(f"Fetching market data for symbol: {symbol}")
        return await self._market_data_client.fetch_market_data(symbol)
