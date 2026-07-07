import pytest

from market_data.assets import resolve_provider_asset_id
from market_data.enums import DataProvider


@pytest.mark.parametrize(
    ("public_input", "provider", "expected"),
    [
        ("BTC", DataProvider.COINGECKO, "bitcoin"),
        ("btc", DataProvider.COINGECKO, "bitcoin"),
        ("bitcoin", DataProvider.COINGECKO, "bitcoin"),
        ("ETH", DataProvider.COINGECKO, "ethereum"),
        ("DOGE", DataProvider.COINCAP, "dogecoin"),
        ("SOL", DataProvider.COINCAP, "solana"),
    ],
)
def test_resolve_provider_asset_id(public_input, provider, expected):
    assert resolve_provider_asset_id(public_input, provider) == expected
