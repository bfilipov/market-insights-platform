import datetime

from fastapi import APIRouter, Depends

from api_gateway.middleware.auth import validate_api_key
from api_gateway.models.responses import HealthResponse
from api_gateway.models.user import User

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
        current_user: User = Depends(validate_api_key),  #
) -> HealthResponse:
    """Health check endpoint — no authentication required."""
    return HealthResponse(
        status="healthy",
        service="api-gateway",
        version="0.1.0",
        timestamp=datetime.datetime.now(datetime.UTC)
    )
