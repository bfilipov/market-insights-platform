import os

import pytest
from httpx import AsyncClient, ASGITransport

# Set test environment variables BEFORE importing app modules
os.environ["MARKET_SIGNAL_HOST"] = "0.0.0.0"
os.environ["MARKET_SIGNAL_PORT"] = "8002"
os.environ["MARKET_DATA_INTERNAL_API_KEY"] = "test-internal-key"
os.environ["LOG_LEVEL"] = "DEBUG"

from market_signal.main import create_app  # noqa: E402


@pytest.fixture
async def client():
    """Async HTTP Client for Service C."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
