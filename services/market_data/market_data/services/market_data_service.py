"""Market Data Service - Business logic orchestration."""

import logging

from market_data.enums import DataProvider
from market_data.models.internal import InternalMarketDataResponse
from market_data.providers.factory import get_provider

logger = logging.getLogger(__name__)


class MarketDataService:
    """
    Service for fetching market data.
    Delegates actual fetching to the chosen Provider (Strategy Pattern).
    """

    async def get_market_data(
            self,
            symbol: str,
            provider: DataProvider | str | None = None
    ) -> InternalMarketDataResponse:
        """
        Get normalized market data.

        Args:
            symbol: The cryptocurrency symbol (e.g., 'bitcoin')
            provider: Optional specific provider to use. Falls back to config default.
        """
        from market_data.config import get_settings
        settings = get_settings()

        # Determine which provider to use
        provider_name = provider if provider else settings.market_data_default_provider
        provider_instance = get_provider(provider_name)

        logger.info(f"Fetching market data for {symbol} via {provider_instance.__class__.__name__}")

        return await provider_instance.fetch_market_data(symbol)
