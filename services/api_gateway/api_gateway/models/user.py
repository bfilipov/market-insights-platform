"""User models for API key management."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    """Represents an API user with an API key."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="User display name")
    email: Optional[str] = Field(None, description="User email address")
    api_key: str = Field(..., description="API key for authentication")
    is_active: bool = Field(True, description="Whether the user is active")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    expires_at: Optional[datetime] = Field(
        None, description="Optional expiration time"
    )
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class UserCreateRequest(BaseModel):
    """Request body for creating a new user."""

    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = Field(None)
    expires_at: Optional[datetime] = Field(None)
    metadata: dict = Field(default_factory=dict)


class UserResponse(BaseModel):
    """User response — excludes the API key for security."""

    id: str
    name: str
    email: Optional[str] = None
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    metadata: dict = {}


class UserWithKeyResponse(UserResponse):
    """User response that includes the API key (only on create/regenerate)."""

    api_key: str
