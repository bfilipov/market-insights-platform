"""
Response models for the API Gateway.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MarketDataResponse(BaseModel):
    """
    Normalized market data response.
    """

    symbol: str = Field(..., description="Asset symbol (e.g., 'bitcoin')")
    name: str = Field(..., description="Full asset name")
    current_price_usd: float = Field(..., description="Current price in USD")
    market_cap_usd: Optional[float] = Field(None, description="Market cap in USD")
    total_volume_usd: Optional[float] = Field(None, description="24h trading volume in USD")
    price_change_24h_usd: Optional[float] = Field(None, description="24h price change in USD")
    price_change_percentage_24h: Optional[float] = Field(
        None, description="24h price change percentage"
    )
    high_24h_usd: Optional[float] = Field(None, description="24h high price in USD")
    low_24h_usd: Optional[float] = Field(None, description="24h low price in USD")
    last_updated: Optional[datetime] = Field(None, description="Last data update timestamp")
    data_source: str = Field(..., description="Source of the market data")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "symbol": "bitcoin",
                    "name": "Bitcoin",
                    "current_price_usd": 43250.75,
                    "market_cap_usd": 847500000000,
                    "price_change_percentage_24h": 2.97,
                    "data_source": "coingecko",
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Standard error response format."""

    detail: str = Field(..., description="Error description")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
