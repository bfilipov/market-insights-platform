import os
from datetime import datetime

import pytest
from httpx import AsyncClient, ASGITransport

# Set test environment variables BEFORE importing app modules
os.environ["MARKET_DATA_INTERNAL_API_KEY"] = "test-internal-key"
os.environ["COINCAP_API_KEY"] = "test-coincap-key"
os.environ["MARKET_DATA_DEFAULT_PROVIDER"] = "coingecko"
os.environ["LOG_LEVEL"] = "DEBUG"

from market_data.config import get_settings  # noqa: E402
from market_data.exceptions import (  # noqa: E402
    AssetNotFoundException,
    ExternalApiUnavailableException,
)
from market_data.main import create_app  # noqa: E402
from market_data.models.internal import InternalMarketDataResponse  # noqa: E402
from market_data.routers.market import get_market_data_service  # noqa: E402
from market_data.services.market_data_service import MarketDataService  # noqa: E402


class MockMarketDataService(MarketDataService):
    """Mock service to avoid actual provider HTTP calls."""

    async def get_market_data(self, symbol, provider=None):
        if symbol == "notfound":
            raise AssetNotFoundException(symbol)
        if symbol == "unavailable":
            raise ExternalApiUnavailableException("mock-provider")

        return InternalMarketDataResponse(
            symbol=symbol,
            name=symbol.capitalize(),
            current_price_usd=100.0,
            market_cap_usd=1000000.0,
            total_volume_usd=50000.0,
            price_change_24h_usd=10.0,
            price_change_percentage_24h=1.5,
            high_24h_usd=105.0,
            low_24h_usd=95.0,
            last_updated=datetime.utcnow(),
            data_source="mock",
        )


@pytest.fixture
def settings():
    return get_settings()


@pytest.fixture
async def client():
    """Async HTTP Client with mocked dependencies."""
    app = create_app()

    # Override the service dependency with our mock
    app.dependency_overrides[get_market_data_service] = lambda: MockMarketDataService()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
