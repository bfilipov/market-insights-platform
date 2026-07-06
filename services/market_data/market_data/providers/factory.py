"""Factory for creating Data Providers."""

import logging
from functools import lru_cache

from market_data.adapters.coincap import CoinCapAdapter
from market_data.adapters.coingecko import CoinGeckoAdapter
from market_data.clients.coincap import CoinCapClient
from market_data.clients.coingecko import CoinGeckoClient
from market_data.enums import DataProvider
from market_data.exceptions import UnsupportedProviderException
from market_data.providers.base import BaseProvider
from market_data.providers.coincap import CoinCapProvider
from market_data.providers.coingecko import CoinGeckoProvider

logger = logging.getLogger(__name__)


@lru_cache()
def _get_coingecko_provider() -> BaseProvider:
    """Cached CoinGecko provider instance."""
    return CoinGeckoProvider(
        client=CoinGeckoClient(),
        adapter=CoinGeckoAdapter()
    )


@lru_cache()
def _get_coincap_provider() -> BaseProvider:
    """Cached CoinCap provider instance."""
    return CoinCapProvider(
        client=CoinCapClient(),
        adapter=CoinCapAdapter()
    )


def get_provider(provider_name: DataProvider | str) -> BaseProvider:
    """
    Factory method to retrieve the appropriate provider.

    Uses cached client instances to maintain connection pooling.
    """
    try:
        provider_enum = DataProvider(provider_name.lower())
    except ValueError:
        raise UnsupportedProviderException(provider_name)

    if provider_enum == DataProvider.COINGECKO:
        return _get_coingecko_provider()
    elif provider_enum == DataProvider.COINCAP:
        return _get_coincap_provider()

    raise UnsupportedProviderException(provider_name)
