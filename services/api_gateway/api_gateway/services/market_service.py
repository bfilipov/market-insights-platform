import logging
from typing import Optional

from api_gateway.clients.market_data_client import MarketDataClient
from api_gateway.clients.market_signal_client import MarketSignalClient
from api_gateway.models.responses import MarketDataResponse, MarketInsightsResponse

logger = logging.getLogger(__name__)


class MarketService:
    def __init__(
            self,
            market_data_client: MarketDataClient,
            market_signal_client: MarketSignalClient
    ):
        self._market_data_client = market_data_client
        self._market_signal_client = market_signal_client

    async def get_market_data(
            self, symbol: str,
            provider: Optional[str] = None
    ) -> MarketDataResponse:
        """Fetch market data only."""
        logger.info(f"Fetching market data for symbol: {symbol}")
        return await self._market_data_client.fetch_market_data(symbol, provider)

    async def get_market_insights(
            self, symbol: str,
            provider: Optional[str] = None
    ) -> MarketInsightsResponse:
        """Fetch market data and augment it with rule-based signals."""
        logger.info(f"Fetching market insights for symbol: {symbol}")

        # 1. Fetch base market data
        market_data = await self._market_data_client.fetch_market_data(symbol, provider)

        # Convert to extended model
        insights = MarketInsightsResponse(**market_data.model_dump())

        # 2. Fetch signal (with graceful degradation)
        try:
            signal = await self._market_signal_client.fetch_signal(
                symbol, market_data.price_change_percentage_24h
            )
            if signal:
                insights.market_signal = signal
                insights.disclaimer = "Rule-based indicator, not financial advice."
        except Exception as e:
            logger.warning(f"Failed to fetch market signal, continuing without it. Error: {e}")

        return insights
