"""Authentication middleware — validates API keys against the user store."""

import hmac
import logging
from typing import Optional

from fastapi import Depends, Header, HTTPException, status

from api_gateway.config import get_settings
from api_gateway.dependencies import get_user_store
from api_gateway.models.user import User
from api_gateway.stores.user_store import UserStore

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
    """Extract and validate the Bearer token from the Authorization header."""
    if not authorization:
        logger.warning("Authentication attempt with missing Authorization header")
        raise AuthenticationError("Missing Authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning(f"Malformed Authorization header: {authorization[:20]}...")
        raise AuthenticationError(
            "Invalid Authorization header format. Expected: Bearer <api_key>"
        )

    return parts[1]


def validate_api_key(
    api_key: str = Depends(extract_bearer_token),
    store: UserStore = Depends(get_user_store),
) -> User:
    """
    Validate the API key against the user store.

    Returns the authenticated ``User`` object so routes can identify
    the caller (useful for logging, rate-limiting, auditing, etc.).
    """
    user = store.authenticate(api_key)

    if user is None:
        logger.warning("Authentication attempt with invalid API key")
        raise AuthenticationError("Invalid API key")

    logger.debug(f"Authenticated user: {user.name} (id={user.id})")
    return user


def validate_admin_api_key(
    authorization: Optional[str] = Header(None),
) -> bool:
    """
    Validate the admin API key.

    Admin endpoints use a separate key (``API_GATEWAY_ADMIN_API_KEY``)
    that is distinct from any regular user key.
    """
    settings = get_settings()

    if not authorization:
        raise AuthenticationError("Missing Authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError(
            "Invalid Authorization header format. Expected: Bearer <api_key>"
        )

    token = parts[1]

    if not hmac.compare_digest(
        token.encode("utf-8"),
        settings.api_gateway_admin_api_key.encode("utf-8"),
    ):
        logger.warning("Admin authentication attempt with invalid API key")
        raise AuthenticationError("Invalid admin API key")

    logger.debug("Admin authenticated successfully")
    return True