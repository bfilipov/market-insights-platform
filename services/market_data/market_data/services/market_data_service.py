import logging
import time

from market_data.assets import resolve_provider_asset_id
from market_data.config import get_settings
from market_data.enums import DataProvider
from market_data.exceptions import UnsupportedProviderException
from market_data.models.internal import InternalMarketDataResponse
from market_data.providers.factory import get_provider

logger = logging.getLogger(__name__)


class MarketDataService:
    # Simple in-memory cache: {"provider:asset_id": (timestamp, data)}
    _cache: dict[str, tuple[float, InternalMarketDataResponse]] = {}
    _cache_ttl_seconds = 60

    @staticmethod
    def _resolve_provider(provider: DataProvider | str | None) -> DataProvider:
        settings = get_settings()

        if provider is None:
            return settings.market_data_default_provider

        if isinstance(provider, DataProvider):
            return provider

        try:
            return DataProvider(provider.lower())
        except ValueError as exc:
            raise UnsupportedProviderException(provider) from exc

    async def get_market_data(
            self,
            symbol: str,
            provider: DataProvider | str | None = None,
    ) -> InternalMarketDataResponse:
        provider_enum = self._resolve_provider(provider)
        provider_asset_id = resolve_provider_asset_id(symbol, provider_enum)

        cache_key = f"{provider_enum.value}:{provider_asset_id}"

        if cache_key in self._cache:
            timestamp, cached_data = self._cache[cache_key]

            if time.time() - timestamp < self._cache_ttl_seconds:
                logger.info("Cache hit for %s", cache_key)
                return cached_data

        provider_instance = get_provider(provider_enum)

        logger.info(
            "Fetching market data for input=%s resolved_asset_id=%s provider=%s",
            symbol,
            provider_asset_id,
            provider_enum.value,
        )

        result = await provider_instance.fetch_market_data(provider_asset_id)

        self._cache[cache_key] = (time.time(), result)

        return result
