"""Base Provider Interface."""

from abc import ABC, abstractmethod

from market_data.models.internal import InternalMarketDataResponse


class BaseProvider(ABC):
    """
    Abstract base class for data providers.
    Implements the Strategy Pattern.
    """

    @abstractmethod
    async def fetch_market_data(self, symbol: str) -> InternalMarketDataResponse:
        """
        Fetch and normalize data for a given symbol.
        """
        ...
