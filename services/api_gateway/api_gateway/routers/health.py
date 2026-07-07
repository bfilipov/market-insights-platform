import datetime
from typing import Any

from fastapi import APIRouter, Depends

from api_gateway.middleware.auth import validate_api_key
from api_gateway.models.responses import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    summary="Health check",
)
async def health_check(
        # All endpoints in Service A must require a valid API key supplied as a bearer token: Authorization: Bearer
        # <key>.
        _auth: Any = Depends(validate_api_key),
) -> HealthResponse:
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="api-gateway",
        version="0.1.0",
        timestamp=datetime.datetime.now(datetime.UTC)
    )
