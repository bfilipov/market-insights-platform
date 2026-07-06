from typing import Optional
from pydantic import BaseModel, Field

class SignalRequest(BaseModel):
    symbol: str = Field(..., description="Asset symbol")
    price_change_percentage_24h: Optional[float] = Field(None, description="24h price change percentage")

class SignalResponse(BaseModel):
    symbol: str
    signal: str = Field(..., description="Rule-based signal: bullish, bearish, or neutral")
    rule_description: str = Field(..., description="Description of the rule applied")
    disclaimer: str = Field(..., description="Disclaimer that this is not financial advice")