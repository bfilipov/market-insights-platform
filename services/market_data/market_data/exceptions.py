"""Custom exceptions for the Market Data Service."""


class BaseMarketDataException(Exception):
    """Base exception for Market Data Service."""

    def __init__(self, detail: str, status_code: int = 500):
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)


class AssetNotFoundException(BaseMarketDataException):
    """Raised when an asset is not found."""

    def __init__(self, symbol: str):
        super().__init__(detail=f"Asset '{symbol}' not found", status_code=404)


class ExternalApiException(BaseMarketDataException):
    """Raised when the external API returns an error."""

    def __init__(self, provider: str, detail: str, status_code: int = 502):
        super().__init__(detail=f"Provider '{provider}' error: {detail}", status_code=status_code)


class ExternalApiUnavailableException(BaseMarketDataException):
    """Raised when the external API is unavailable."""

    def __init__(self, provider: str):
        super().__init__(detail=f"Provider '{provider}' is temporarily unavailable", status_code=503)


class UnsupportedProviderException(BaseMarketDataException):
    """Raised when a requested provider is not supported."""

    def __init__(self, provider: str):
        super().__init__(detail=f"Provider '{provider}' is not supported", status_code=400)
