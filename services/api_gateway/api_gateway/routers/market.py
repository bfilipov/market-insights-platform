"""Market data router."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api_gateway.dependencies import get_market_service
from api_gateway.exceptions import (
    AssetNotFoundException,
    ExternalServiceException,
    ServiceUnavailableException,
)
from api_gateway.middleware.auth import validate_api_key
from api_gateway.models.responses import MarketDataResponse, MarketInsightsResponse
from api_gateway.models.user import User
from api_gateway.services.market_service import MarketService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["market"])


@router.get(
    "/market/{symbol}",
    response_model=MarketDataResponse,
    responses={
        401: {"description": "Invalid or missing API key"},
        404: {"description": "Asset not found"},
        502: {"description": "External service error"},
        503: {"description": "Service unavailable"},
    },
    summary="Get market data for an asset",
)
async def get_market_data(
        symbol: str,
        provider: Optional[str] = Query(
            None,
            description="Override default data provider (e.g., 'coingecko', 'coincap')",
        ),
        current_user: User = Depends(validate_api_key),
        market_service: MarketService = Depends(get_market_service),
) -> MarketDataResponse:
    """Get market data for a cryptocurrency asset."""
    try:
        logger.info(
            f"User '{current_user.name}' (id={current_user.id}) "
            f"requesting market data for '{symbol}'"
        )
        return await market_service.get_market_data(symbol, provider=provider)
    except AssetNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
    except ServiceUnavailableException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=e.detail
        )
    except ExternalServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=e.detail
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_market_data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/market/{symbol}/insights",
    response_model=MarketInsightsResponse,
    responses={
        401: {"description": "Invalid or missing API key"},
        404: {"description": "Asset not found"},
        502: {"description": "External service error"},
        503: {"description": "Service unavailable"},
    },
    summary="Get market data with rule-based signals",
)
async def get_market_insights(
        symbol: str,
        provider: Optional[str] = Query(
            None, description="Override default data provider (e.g., 'coingecko', 'coincap')"
        ),
        current_user: User = Depends(validate_api_key),
        market_service: MarketService = Depends(get_market_service),
) -> MarketInsightsResponse:
    """Get market data augmented with a rule-based market signal."""
    try:
        return await market_service.get_market_insights(symbol, provider=provider)
    except AssetNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
    except ServiceUnavailableException as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=e.detail)
    except ExternalServiceException as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=e.detail)
    except Exception as e:
        logger.exception(f"Unexpected error in get_market_insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
