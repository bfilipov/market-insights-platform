import hmac
import logging
from typing import Optional

from fastapi import Depends, Header, HTTPException, status

from api_gateway.config import get_settings

logger = logging.getLogger(__name__)


class AuthenticationError(HTTPException):
    """Custom HTTP exception for authentication failures."""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


def extract_bearer_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Extract and validate Bearer token from Authorization header.

    Args:
        authorization: The raw Authorization header value

    Returns:
        The extracted API key

    Raises:
        AuthenticationError: If the header is missing or malformed
    """
    if not authorization:
        logger.warning("Authentication attempt with missing Authorization header")
        raise AuthenticationError("Missing Authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning(
            f"Malformed Authorization header: {authorization[:20]}..."
        )
        raise AuthenticationError(
            "Invalid Authorization header format. Expected: Bearer <api_key>"
        )

    return parts[1]


def validate_api_key(api_key: str = Depends(extract_bearer_token)) -> str:
    """
    Validate the extracted API key against the configured expected key.

    This is implemented as a FastAPI dependency, allowing it to be
    injected into any route that requires authentication.

    Args:
        api_key: The API key extracted from the header

    Returns:
        The validated API key

    Raises:
        AuthenticationError: If the API key doesn't match
    """
    settings = get_settings()

    # Use constant-time comparison to prevent timing attacks
    if not _constant_time_compare(api_key, settings.api_gateway_api_key):
        logger.warning("Authentication attempt with invalid API key")
        raise AuthenticationError("Invalid API key")

    logger.debug("Successfully authenticated request")
    return api_key


def _constant_time_compare(a: str, b: str) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.

    Args:
        a: First string to compare
        b: Second string to compare

    Returns:
        True if strings are equal, False otherwise
    """
    return hmac.compare_digest(a.encode(), b.encode())
