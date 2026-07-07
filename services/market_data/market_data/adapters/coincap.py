"""Adapter for CoinCap responses."""

from datetime import datetime, timezone
from typing import Dict

from market_data.adapters.base import BaseAdapter
from market_data.exceptions import AssetNotFoundException
from market_data.models.coincap import CoinCapResponse
from market_data.models.internal import InternalMarketDataResponse


class CoinCapAdapter(BaseAdapter):
    """Adapts CoinCap format to Internal format."""

    def adapt(self, raw_data: Dict) -> InternalMarketDataResponse:
        try:
            external = CoinCapResponse(**raw_data)
        except Exception:
            raise AssetNotFoundException("unknown")

        if external.data is None:
            raise AssetNotFoundException("unknown")

        data = external.data

        # CoinCap provides prices as strings, we must safely convert them
        price = self._safe_float(data.price_usd)
        if price is None:
            raise AssetNotFoundException(data.id)

        return InternalMarketDataResponse(
            symbol=data.symbol.lower(),
            name=data.name,
            current_price_usd=price,
            market_cap_usd=self._safe_float(data.market_cap_usd),
            total_volume_usd=self._safe_float(data.volume_usd_24_hr),
            price_change_percentage_24h=self._safe_float(data.change_percent_24_hr),
            # CoinCap doesn't provide 24h high/low or absolute price change in this endpoint
            high_24h_usd=None,
            low_24h_usd=None,
            price_change_24h_usd=None,
            last_updated=self._parse_timestamp(external.timestamp),
            data_source="coincap",
        )

    def _parse_timestamp(self, ts_ms: int | None) -> datetime | None:
        if not ts_ms:
            return None
        try:
            return datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc)
        except (ValueError, OSError):
            return None
