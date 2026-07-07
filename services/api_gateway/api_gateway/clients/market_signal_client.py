import logging
from typing import Optional

import httpx

from api_gateway.clients.base import BaseServiceClient
from api_gateway.exceptions import ExternalServiceException
from api_gateway.models.responses import MarketSignal

logger = logging.getLogger(__name__)


class MarketSignalClient(BaseServiceClient[MarketSignal]):
    def _get_base_url(self) -> str:
        return self._settings.market_signal_service_url

    def _get_api_key(self) -> str:
        return self._settings.services_internal_api_key

    async def fetch_signal(self, symbol: str, price_change_percentage_24h: Optional[float]) -> Optional[MarketSignal]:
        if price_change_percentage_24h is None:
            return None

        try:
            payload = {
                "symbol": symbol,
                "price_change_percentage_24h": price_change_percentage_24h
            }
            data = await self._post("/api/v1/signal", json=payload)
            return MarketSignal(signal=data["signal"], rule_description=data["rule_description"])
        except httpx.HTTPStatusError as e:
            logger.error(f"Market Signal Service error: {e.response.status_code}")
            raise ExternalServiceException("market-signal", f"HTTP {e.response.status_code}")
        except Exception as e:
            logger.exception(f"Unexpected error calling Market Signal Service: {e}")
            raise ExternalServiceException("market-signal", str(e))

    async def fetch(self, **kwargs) -> MarketSignal:
        pass  # Not used, explicit fetch_signal method preferred
