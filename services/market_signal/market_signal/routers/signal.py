import logging

from fastapi import APIRouter, Depends, Header, HTTPException, status

from market_signal.config import get_settings
from market_signal.models import SignalRequest, SignalResponse
from market_signal.services.signal_service import MarketSignalService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["signal"])


def validate_internal_api_key(authorization: str = Header(None)) -> bool:
    settings = get_settings()
    if not authorization or authorization.split(" ", 1)[-1] != settings.market_signal_internal_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
    return True


@router.post("/signal", response_model=SignalResponse)
async def get_market_signal(
        request: SignalRequest,
        _auth: bool = Depends(validate_internal_api_key)
):
    service = MarketSignalService()
    return service.calculate_signal(request)
