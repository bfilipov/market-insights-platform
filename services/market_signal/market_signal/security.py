import hmac
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from market_signal.config import get_settings

internal_bearer = HTTPBearer(auto_error=False)


def validate_internal_api_key(
        credentials: Annotated[
            HTTPAuthorizationCredentials | None,
            Depends(internal_bearer),
        ],
) -> bool:
    settings = get_settings()

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not hmac.compare_digest(
            credentials.credentials,
            settings.services_internal_api_key,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True
