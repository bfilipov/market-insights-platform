"""External API response models for CoinGecko."""

from typing import Optional

from pydantic import BaseModel


class CoinGeckoMarketData(BaseModel):
    """Market data section of CoinGecko response."""
    current_price: Optional[dict[str, float]] = None
    market_cap: Optional[dict[str, float]] = None
    total_volume: Optional[dict[str, float]] = None
    price_change_24h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    high_24h: Optional[dict[str, float]] = None
    low_24h: Optional[dict[str, float]] = None


class CoinGeckoResponse(BaseModel):
    """Raw response from CoinGecko /coins/{id} endpoint."""
    id: str
    symbol: str
    name: str
    market_data: Optional[CoinGeckoMarketData] = None
    last_updated: Optional[str] = None
