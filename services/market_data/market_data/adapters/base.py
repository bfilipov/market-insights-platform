"""Base Adapter Interface."""

from abc import ABC, abstractmethod
from typing import Dict

from market_data.models.internal import InternalMarketDataResponse


class BaseAdapter(ABC):
    """Abstract base class for data adapters."""

    @abstractmethod
    def adapt(self, raw_data: Dict) -> InternalMarketDataResponse:
        """
        Transform raw external API data into the internal schema.
        """
        ...

    def _safe_float(self, value: str | None) -> float | None:
        """Safely convert string numbers to float."""
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None