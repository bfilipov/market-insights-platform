import pytest

from market_data.adapters.coincap import CoinCapAdapter
from market_data.adapters.coingecko import CoinGeckoAdapter
from market_data.exceptions import AssetNotFoundException


def test_coingecko_adapter_success():
    adapter = CoinGeckoAdapter()
    raw_data = {
        "id": "bitcoin",
        "symbol": "BTC",
        "name": "Bitcoin",
        "market_data": {
            "current_price": {"usd": 50000.0},
            "market_cap": {"usd": 1000000000.0},
            "total_volume": {"usd": 50000000.0},
            "price_change_24h": 1000.0,
            "price_change_percentage_24h": 2.0,
            "high_24h": {"usd": 51000.0},
            "low_24h": {"usd": 49000.0}
        },
        "last_updated": "2023-10-01T12:00:00Z"
    }

    result = adapter.adapt(raw_data)

    assert result.symbol == "btc"
    assert result.name == "Bitcoin"
    assert result.current_price_usd == 50000.0
    assert result.market_cap_usd == 1000000000.0
    assert result.data_source == "coingecko"


def test_coingecko_adapter_missing_price():
    adapter = CoinGeckoAdapter()
    raw_data = {
        "id": "fakecoin",
        "symbol": "FAKE",
        "name": "Fake Coin",
        "market_data": {
            "current_price": {"eur": 10.0},  # Missing USD
        }
    }

    with pytest.raises(AssetNotFoundException):
        adapter.adapt(raw_data)


def test_coincap_adapter_success():
    adapter = CoinCapAdapter()
    raw_data = {
        "data": {
            "id": "bitcoin",
            "symbol": "BTC",
            "name": "Bitcoin",
            "priceUsd": "50000.5",
            "marketCapUsd": "1000000000.1",
            "volumeUsd24Hr": "50000000.2",
            "changePercent24Hr": "2.5",
            "vwap24Hr": "49500.0"
        },
        "timestamp": 1696161600000
    }

    result = adapter.adapt(raw_data)

    assert result.symbol == "btc"
    assert result.name == "Bitcoin"
    assert result.current_price_usd == 50000.5
    assert result.market_cap_usd == 1000000000.1
    assert result.price_change_percentage_24h == 2.5
    assert result.data_source == "coincap"
    assert result.last_updated is not None


def test_coincap_adapter_missing_data():
    adapter = CoinCapAdapter()
    raw_data = {
        "data": None,
        "timestamp": 1696161600000
    }

    with pytest.raises(AssetNotFoundException):
        adapter.adapt(raw_data)


def test_coincap_adapter_malformed_price():
    adapter = CoinCapAdapter()
    raw_data = {
        "data": {
            "id": "bitcoin",
            "symbol": "BTC",
            "name": "Bitcoin",
            "priceUsd": "not-a-number",  # Malformed float
        },
        "timestamp": 1696161600000
    }

    # The adapter's _safe_float should handle this gracefully by returning None,
    # which in turn triggers an AssetNotFoundException if the primary price is missing.
    with pytest.raises(AssetNotFoundException):
        adapter.adapt(raw_data)
