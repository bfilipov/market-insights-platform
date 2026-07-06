"""Internal response models - The stable schema exposed to Service A."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class InternalMarketDataResponse(BaseModel):
    """Internal normalized market data response."""
    symbol: str = Field(..., description="Normalized lowercase symbol")
    name: str = Field(..., description="Full asset name")
    current_price_usd: float = Field(..., description="Current price in USD")
    market_cap_usd: Optional[float] = Field(None, description="Market cap in USD")
    total_volume_usd: Optional[float] = Field(None, description="24h trading volume")
    price_change_24h_usd: Optional[float] = Field(None, description="24h price change")
    price_change_percentage_24h: Optional[float] = Field(None, description="24h price change %")
    high_24h_usd: Optional[float] = Field(None, description="24h high")
    low_24h_usd: Optional[float] = Field(None, description="24h low")
    last_updated: Optional[datetime] = Field(None, description="Last update time")
    data_source: str = Field(..., description="Identifier for the data source")
