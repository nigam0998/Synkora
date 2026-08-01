"""
Synkora API — Auth Schemas

Pydantic models for authentication request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ── Request Schemas ───────────────────────────────────────────────────


class RegisterRequest(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Schema for refreshing an access token."""

    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Schema for changing password."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


# ── Response Schemas ──────────────────────────────────────────────────


class TokenResponse(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    """Schema for user data in responses."""

    id: str
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    github_connected: bool = False
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Combined auth response with tokens and user data."""

    tokens: TokenResponse
    user: UserResponse


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    success: bool = True
