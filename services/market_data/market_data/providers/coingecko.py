"""CoinGecko Data Provider."""

import logging

from market_data.adapters.coingecko import CoinGeckoAdapter
from market_data.clients.coingecko import CoinGeckoClient
from market_data.models.internal import InternalMarketDataResponse
from market_data.providers.base import BaseProvider

logger = logging.getLogger(__name__)


class CoinGeckoProvider(BaseProvider):
    """Provider orchestrating CoinGecko Client and Adapter."""

    def __init__(self, client: CoinGeckoClient, adapter: CoinGeckoAdapter):
        self._client = client
        self._adapter = adapter

    async def fetch_market_data(self, symbol: str) -> InternalMarketDataResponse:
        logger.info(f"Fetching from CoinGecko for: {symbol}")
        raw_data = await self._client.get_coin_data(symbol)
        return self._adapter.adapt(raw_data)
