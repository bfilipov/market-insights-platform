"""
Market data router.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from api_gateway.dependencies import get_market_service
from api_gateway.exceptions import (
    AssetNotFoundException,
    ExternalServiceException,
    ServiceUnavailableException,
)
from api_gateway.middleware.auth import validate_api_key
from api_gateway.models.responses import (
    HealthResponse,
    MarketDataResponse,
)
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
    description="Retrieves current market data for the specified cryptocurrency symbol.",
)
async def get_market_data(
        symbol: str,
        provider: Optional[str] = Query(
            None,
            description="Override default data provider (e.g., 'coingecko', 'coincap')"
        ),
        _api_key: str = Depends(validate_api_key),
        market_service: MarketService = Depends(get_market_service),
) -> MarketDataResponse:
    """
    Get market data for a cryptocurrency asset.

    Args:
        symbol: The cryptocurrency symbol (e.g., 'bitcoin', 'ethereum')
        provider: Override default data provider (e.g., 'coingecko', 'coincap')
        _api_key: Validated API key (injected)
        market_service: Market service (injected)

    Returns:
        Normalized market data

    Raises:
        HTTPException: For various error conditions
    """
    try:
        return await market_service.get_market_data(symbol, provider=provider)
    except AssetNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
    except ServiceUnavailableException as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=e.detail)
    except ExternalServiceException as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=e.detail)
    except Exception as e:
        logger.exception(f"Unexpected error in get_market_data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


# Health endpoint (no authentication required)
@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    summary="Health check",
    description="Returns the health status of the API Gateway service.",
)
async def health_check() -> HealthResponse:
    """Health check endpoint - no authentication required."""
    from datetime import datetime

    return HealthResponse(
        status="healthy",
        service="api-gateway",
        version="1.0.0",
        timestamp=datetime.utcnow(),
    )
