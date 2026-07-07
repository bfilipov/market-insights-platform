import logging

from fastapi import APIRouter, Depends

from market_signal.models import SignalRequest, SignalResponse
from market_signal.security import validate_internal_api_key
from market_signal.services.signal_service import MarketSignalService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["signal"])


@router.post("/signal", response_model=SignalResponse)
async def get_market_signal(
        request: SignalRequest,
        _auth: bool = Depends(validate_internal_api_key)
):
    service = MarketSignalService()
    return service.calculate_signal(request)
