"""Market data router for the Market Data Service."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status

from market_data.config import get_settings
from market_data.enums import DataProvider
from market_data.exceptions import (
    AssetNotFoundException,
    ExternalApiUnavailableException,
    UnsupportedProviderException,
)
from market_data.models.internal import InternalMarketDataResponse
from market_data.services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["market"])


def validate_internal_api_key(
        authorization: Optional[str] = Header(None),
) -> bool:
    settings = get_settings()
    if not authorization or authorization.split(" ", 1)[-1] != settings.services_internal_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
    return True


def get_market_data_service() -> MarketDataService:
    return MarketDataService()


@router.get(
    "/market/{symbol}",
    response_model=InternalMarketDataResponse,
    responses={401: {}, 404: {}, 503: {}},
    summary="Get market data for an asset",
)
async def get_market_data(
        symbol: str,
        provider: Optional[DataProvider] = None,
        _auth: bool = Depends(validate_internal_api_key),
        service: MarketDataService = Depends(get_market_data_service),
) -> InternalMarketDataResponse:
    """
    Fetches market data.
    Optionally specify `?provider=coincap` to override the default data source.
    """
    try:
        return await service.get_market_data(symbol, provider=provider)
    except AssetNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
    except UnsupportedProviderException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)
    except ExternalApiUnavailableException as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=e.detail)
