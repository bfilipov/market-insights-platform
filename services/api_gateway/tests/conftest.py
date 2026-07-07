import os
from datetime import datetime

import pytest
from httpx import AsyncClient, ASGITransport

from api_gateway.exceptions import ExternalServiceException  # noqa: E402

# Set test environment variables BEFORE importing app modules
os.environ["API_GATEWAY_HOST"] = "0.0.0.0"
os.environ["API_GATEWAY_PORT"] = "8000"
os.environ["API_GATEWAY_ADMIN_API_KEY"] = "test-admin-key"
os.environ["API_KEYS_FILE"] = "/tmp/test_users.json"  # Overridden per-test
os.environ["MARKET_DATA_SERVICE_URL"] = "http://localhost:8001"
os.environ["SERVICES_INTERNAL_API_KEY"] = "test-internal-key"
os.environ["LOG_LEVEL"] = "DEBUG"

from api_gateway.config import get_settings  # noqa: E402
from api_gateway.dependencies import (  # noqa: E402
    get_user_store,
    get_market_service,
    get_market_data_client,
)
from api_gateway.main import create_app  # noqa: E402
from api_gateway.models.responses import MarketDataResponse, MarketSignal  # noqa: E402
from api_gateway.services.market_service import MarketService  # noqa: E402
from api_gateway.stores.user_store import UserStore  # noqa: E402


@pytest.fixture
def settings(tmp_path, monkeypatch):
    """Clear settings cache and point to a temp users file."""
    get_settings.cache_clear()
    get_user_store.cache_clear()
    get_market_data_client.cache_clear()

    monkeypatch.setenv("API_KEYS_FILE", str(tmp_path / "users.json"))
    return get_settings()


@pytest.fixture
def user_store(settings):
    """Provides a fresh UserStore for each test."""
    return UserStore(settings.api_keys_file)


class MockMarketDataClient:
    """Mock client to avoid real HTTP calls to the Market Data Service."""

    async def fetch_market_data(self, symbol, provider=None):
        return MarketDataResponse(
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

    async def close(self):
        pass


class MockMarketSignalClient:
    """Mock client for Service C."""

    def __init__(self, fail=False):
        self._fail = fail

    async def fetch_signal(self, symbol, price_change_percentage_24h):
        if self._fail:
            raise ExternalServiceException("market-signal", "simulated failure")
        if price_change_percentage_24h is None:
            return None
        return MarketSignal(signal="bullish", rule_description="mock rule")

    async def close(self):
        pass


@pytest.fixture
def mock_market_signal_client_success():
    return MockMarketSignalClient(fail=False)


@pytest.fixture
def mock_market_signal_client_fail():
    return MockMarketSignalClient(fail=True)


@pytest.fixture
def mock_market_service():
    return MarketService(market_data_client=MockMarketDataClient())


@pytest.fixture
async def client(settings, user_store, mock_market_service):
    """Async HTTP Client with overridden dependencies."""
    app = create_app()

    # Override FastAPI dependencies
    app.dependency_overrides[get_user_store] = lambda: user_store
    app.dependency_overrides[get_market_service] = lambda: mock_market_service

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
