"""CoinCap Data Provider."""

import logging

from market_data.adapters.coincap import CoinCapAdapter
from market_data.clients.coincap import CoinCapClient
from market_data.models.internal import InternalMarketDataResponse
from market_data.providers.base import BaseProvider

logger = logging.getLogger(__name__)


class CoinCapProvider(BaseProvider):
    """Provider orchestrating CoinCap Client and Adapter."""

    def __init__(self, client: CoinCapClient, adapter: CoinCapAdapter):
        self._client = client
        self._adapter = adapter

    async def fetch_market_data(self, symbol: str) -> InternalMarketDataResponse:
        logger.info(f"Fetching from CoinCap for: {symbol}")
        raw_data = await self._client.get_asset_data(symbol)
        return self._adapter.adapt(raw_data)