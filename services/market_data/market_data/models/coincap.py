"""External API response models for CoinCap."""

from typing import Optional

from pydantic import BaseModel, Field


class CoinCapAssetData(BaseModel):
    """Data payload from CoinCap /assets/{id} endpoint."""
    id: str
    symbol: str
    name: str
    # CoinCap returns prices as strings!
    price_usd: Optional[str] = Field(None, alias="priceUsd")
    market_cap_usd: Optional[str] = Field(None, alias="marketCapUsd")
    volume_usd_24_hr: Optional[str] = Field(None, alias="volumeUsd24Hr")
    change_percent_24_hr: Optional[str] = Field(None, alias="changePercent24Hr")
    vwap_24_hr: Optional[str] = Field(None, alias="vwap24Hr")
    explorer: Optional[str] = None

    model_config = {"populate_by_name": True}


class CoinCapResponse(BaseModel):
    """Wrapper for CoinCap response."""
    data: Optional[CoinCapAssetData] = None
    timestamp: Optional[int] = None
