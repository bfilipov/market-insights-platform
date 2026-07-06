"""Adapter for CoinGecko responses."""

from datetime import datetime
from typing import Dict

from market_data.adapters.base import BaseAdapter
from market_data.exceptions import AssetNotFoundException
from market_data.models.coingecko import CoinGeckoResponse
from market_data.models.internal import InternalMarketDataResponse


class CoinGeckoAdapter(BaseAdapter):
    """Adapts CoinGecko format to Internal format."""

    def adapt(self, raw_data: Dict) -> InternalMarketDataResponse:
        try:
            external = CoinGeckoResponse(**raw_data)
        except Exception as e:
            raise AssetNotFoundException("unknown")

        if external.market_data is None:
            raise AssetNotFoundException(external.id)

        md = external.market_data
        price = self._extract_usd(md.current_price)
        if price is None:
            raise AssetNotFoundException(external.id)

        return InternalMarketDataResponse(
            symbol=external.symbol.lower(),
            name=external.name,
            current_price_usd=price,
            market_cap_usd=self._extract_usd(md.market_cap),
            total_volume_usd=self._extract_usd(md.total_volume),
            price_change_24h_usd=md.price_change_24h,
            price_change_percentage_24h=md.price_change_percentage_24h,
            high_24h_usd=self._extract_usd(md.high_24h),
            low_24h_usd=self._extract_usd(md.low_24h),
            last_updated=self._parse_timestamp(external.last_updated),
            data_source="coingecko",
        )

    def _extract_usd(self, prices: Dict | None) -> float | None:
        return prices.get("usd") if prices else None

    def _parse_timestamp(self, ts: str | None) -> datetime | None:
        if not ts:
            return None
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            return None
