"""
Custom exception classes for the API Gateway service.
"""


class BaseApiException(Exception):
    """Base exception for all API exceptions."""

    def __init__(self, detail: str, status_code: int = 500):
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)


class AuthenticationException(BaseApiException):
    """Raised when authentication fails."""

    def __init__(self, detail: str = "Invalid or missing API key"):
        super().__init__(detail=detail, status_code=401)


class AssetNotFoundException(BaseApiException):
    """Raised when a requested asset is not found."""

    def __init__(self, symbol: str):
        super().__init__(
            detail=f"Asset '{symbol}' not found",
            status_code=404,
        )


class ExternalServiceException(BaseApiException):
    """Raised when an external service call fails."""

    def __init__(self, service: str, detail: str):
        super().__init__(
            detail=f"External service '{service}' error: {detail}",
            status_code=502,
        )


class ServiceUnavailableException(BaseApiException):
    """Raised when a required service is unavailable."""

    def __init__(self, service: str):
        super().__init__(
            detail=f"Service '{service}' is temporarily unavailable",
            status_code=503,
        )


class RateLimitExceededException(BaseApiException):
    """Raised when rate limit is exceeded."""

    def __init__(self, detail: str = "Rate limit exceeded. Please try again later."):
        super().__init__(detail=detail, status_code=429)
