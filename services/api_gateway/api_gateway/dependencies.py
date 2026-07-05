"""
Dependency injection configuration.
"""

from functools import lru_cache

from api_gateway.clients.market_data_client import MarketDataClient
from api_gateway.services.market_service import MarketService


@lru_cache()
def get_market_data_client() -> MarketDataClient:
    """
    Get a cached Market Data Client instance.

    Uses lru_cache to implement Singleton pattern for the client.
    """
    return MarketDataClient()


def get_market_service() -> MarketService:
    """
    Get a Market Service instance with its dependencies injected.

    This demonstrates the Dependency Injection pattern, where
    the service receives its dependencies rather than creating them.
    """
    return MarketService(
        market_data_client=get_market_data_client(),
    )
