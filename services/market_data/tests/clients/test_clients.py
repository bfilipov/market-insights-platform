from unittest.mock import AsyncMock

import httpx
import pytest

from market_data.clients.coincap import CoinCapClient
from market_data.clients.coingecko import CoinGeckoClient
from market_data.exceptions import AssetNotFoundException, ExternalApiUnavailableException


@pytest.fixture
def coingecko_client():
    client = CoinGeckoClient()
    # Mock the resilient _get method to bypass actual HTTP calls and tenacity retries
    client._get = AsyncMock()
    return client


@pytest.fixture
def coincap_client():
    client = CoinCapClient()
    client._get = AsyncMock()
    return client


async def test_coingecko_success(coingecko_client):
    coingecko_client._get.return_value = {"id": "bitcoin", "symbol": "btc"}
    result = await coingecko_client.get_coin_data("bitcoin")
    assert result["symbol"] == "btc"


async def test_coingecko_404_raises_asset_not_found(coingecko_client):
    request = httpx.Request("GET", "https://test.com")
    response = httpx.Response(404, request=request)

    coingecko_client._get.side_effect = httpx.HTTPStatusError(
        "Not Found", request=request, response=response
    )

    with pytest.raises(AssetNotFoundException):
        await coingecko_client.get_coin_data("fakecoin")


async def test_coingecko_500_raises_external_unavailable(coingecko_client):
    request = httpx.Request("GET", "https://test.com")
    response = httpx.Response(500, request=request)

    coingecko_client._get.side_effect = httpx.HTTPStatusError(
        "Server Error", request=request, response=response
    )

    with pytest.raises(ExternalApiUnavailableException):
        await coingecko_client.get_coin_data("bitcoin")


async def test_coingecko_connect_error_raises_external_unavailable(coingecko_client):
    coingecko_client._get.side_effect = httpx.ConnectError("Connection refused")

    with pytest.raises(ExternalApiUnavailableException):
        await coingecko_client.get_coin_data("bitcoin")


async def test_coincap_success(coincap_client):
    coincap_client._get.return_value = {"data": {"id": "bitcoin"}}
    result = await coincap_client.get_asset_data("bitcoin")
    assert result["data"]["id"] == "bitcoin"


async def test_coincap_404_raises_asset_not_found(coincap_client):
    request = httpx.Request("GET", "https://test.com")
    response = httpx.Response(404, request=request)

    coincap_client._get.side_effect = httpx.HTTPStatusError(
        "Not Found", request=request, response=response
    )

    with pytest.raises(AssetNotFoundException):
        await coincap_client.get_asset_data("fakecoin")
