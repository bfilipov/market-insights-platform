import logging
import time

from market_data.enums import DataProvider
from market_data.models.internal import InternalMarketDataResponse
from market_data.providers.factory import get_provider

logger = logging.getLogger(__name__)

class MarketDataService:
    # Simple in-memory cache: { "symbol:provider": (timestamp, data) }
    _cache = {}
    _cache_ttl_seconds = 60  # 1 minute TTL

    async def get_market_data(
            self,
            symbol: str,
            provider: DataProvider | str | None = None
    ) -> InternalMarketDataResponse:
        from market_data.config import get_settings
        settings = get_settings()

        provider_name = provider if provider else settings.market_data_default_provider
        cache_key = f"{symbol}:{provider_name}"

        # Check cache
        if cache_key in self._cache:
            timestamp, cached_data = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl_seconds:
                logger.info(f"Cache hit for {cache_key}")
                return cached_data

        provider_instance = get_provider(provider_name)
        logger.info(f"Fetching market data for {symbol} via {provider_instance.__class__.__name__}")
        
        result = await provider_instance.fetch_market_data(symbol)
        
        # Save to cache
        self._cache[cache_key] = (time.time(), result)
        return result