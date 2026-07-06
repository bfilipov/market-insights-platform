import logging
from market_signal.models import SignalRequest, SignalResponse

logger = logging.getLogger(__name__)


class MarketSignalService:
    def calculate_signal(self, request: SignalRequest) -> SignalResponse:
        change = request.price_change_percentage_24h

        if change is None:
            signal = "neutral"
            rule = "Insufficient data (24h change missing)"
        elif change > 2.0:
            signal = "bullish"
            rule = f"24h change is +{change:.2f}% (> +2%)"
        elif change < -2.0:
            signal = "bearish"
            rule = f"24h change is {change:.2f}% (< -2%)"
        else:
            signal = "neutral"
            rule = f"24h change is {change:.2f}% (between -2% and +2%)"

        return SignalResponse(
            symbol=request.symbol,
            signal=signal,
            rule_description=rule,
            disclaimer="This is a rule-based indicator generated from recent market data and is not financial advice."
        )