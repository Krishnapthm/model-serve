"""Pydantic schemas for user authentication."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SignupRequest(BaseModel):
    """Request body for POST /auth/signup."""

    email: str
    password: str = Field(min_length=8)
    full_name: str | None = None


class LoginRequest(BaseModel):
    """Request body for POST /auth/login."""

    email: str
    password: str = Field(min_length=8)


class UserRead(BaseModel):
    """Response schema for user identity information."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str | None = None
    created_at: datetime
    is_active: bool


class AuthSession(BaseModel):
    """Auth response payload containing bearer token and user profile."""

    access_token: str
    token_type: str = "bearer"
    user: UserRead
