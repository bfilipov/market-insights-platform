"""Admin router — user management endpoints."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from api_gateway.dependencies import get_user_store
from api_gateway.middleware.auth import validate_admin_api_key
from api_gateway.models.user import (
    UserCreateRequest,
    UserResponse,
    UserWithKeyResponse,
)
from api_gateway.stores.user_store import UserStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="List all API users",
    dependencies=[Depends(validate_admin_api_key)],
)
async def list_users(store: UserStore = Depends(get_user_store)):
    """List all registered API users (API keys are excluded)."""
    return [UserResponse(**u.model_dump()) for u in store.list_users()]


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Get a specific user",
    dependencies=[Depends(validate_admin_api_key)],
)
async def get_user(
    user_id: str,
    store: UserStore = Depends(get_user_store),
):
    user = store.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found",
        )
    return UserResponse(**user.model_dump())


@router.post(
    "/users",
    response_model=UserWithKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new API user",
    dependencies=[Depends(validate_admin_api_key)],
)
async def create_user(
    request: UserCreateRequest,
    store: UserStore = Depends(get_user_store),
):
    """
    Create a new API user.

    The generated API key is returned **only** in this response.
    Store it securely — it cannot be retrieved later.
    """
    user = store.add_user(
        name=request.name,
        email=request.email,
        expires_at=request.expires_at,
        metadata=request.metadata,
    )
    return UserWithKeyResponse(**user.model_dump())


@router.delete(
    "/users/{user_id}",
    summary="Delete an API user",
    dependencies=[Depends(validate_admin_api_key)],
)
async def delete_user(
    user_id: str,
    store: UserStore = Depends(get_user_store),
):
    if not store.remove_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found",
        )
    return {"detail": f"User '{user_id}' deleted"}


@router.patch(
    "/users/{user_id}/deactivate",
    response_model=UserResponse,
    summary="Deactivate a user (key is rejected but not deleted)",
    dependencies=[Depends(validate_admin_api_key)],
)
async def deactivate_user(
    user_id: str,
    store: UserStore = Depends(get_user_store),
):
    if not store.deactivate_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found",
        )
    user = store.get_user(user_id)
    return UserResponse(**user.model_dump())


@router.post(
    "/users/{user_id}/regenerate-key",
    response_model=UserWithKeyResponse,
    summary="Regenerate API key for a user",
    dependencies=[Depends(validate_admin_api_key)],
)
async def regenerate_api_key(
    user_id: str,
    store: UserStore = Depends(get_user_store),
):
    """
    Issue a new API key for an existing user.

    The old key immediately stops working. The new key is returned
    **only** in this response.
    """
    user = store.regenerate_api_key(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found",
        )
    return UserWithKeyResponse(**user.model_dump())