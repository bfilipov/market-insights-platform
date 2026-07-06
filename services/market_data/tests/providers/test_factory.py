import pytest

from market_data.exceptions import UnsupportedProviderException
from market_data.providers.coincap import CoinCapProvider
from market_data.providers.coingecko import CoinGeckoProvider
from market_data.providers.factory import get_provider


def test_get_coingecko_provider():
    provider = get_provider("coingecko")
    assert isinstance(provider, CoinGeckoProvider)


def test_get_coincap_provider():
    provider = get_provider("coincap")
    assert isinstance(provider, CoinCapProvider)


def test_get_invalid_provider_raises_exception():
    with pytest.raises(UnsupportedProviderException):
        get_provider("invalid_provider_name")


def test_get_provider_is_cached():
    # Because of @lru_cache, calling it twice should return the exact same instance
    provider1 = get_provider("coingecko")
    provider2 = get_provider("coingecko")
    assert provider1 is provider2
