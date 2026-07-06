"""Dependency injection configuration."""

from functools import lru_cache

from api_gateway.clients.market_data_client import MarketDataClient
from api_gateway.config import get_settings
from api_gateway.services.market_service import MarketService
from api_gateway.stores.user_store import UserStore


@lru_cache()
def get_user_store() -> UserStore:
    """Get a cached UserStore instance (Singleton)."""
    settings = get_settings()
    return UserStore(settings.api_keys_file)


@lru_cache()
def get_market_data_client() -> MarketDataClient:
    """Get a cached Market Data Client instance."""
    return MarketDataClient()


def get_market_service() -> MarketService:
    """Get a Market Service instance with dependencies injected."""
    return MarketService(
        market_data_client=get_market_data_client(),
    )