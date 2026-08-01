"""
Synkora API — Authentication Router

Handles user registration, login, token refresh, logout, and profile retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest):
    """
    Register a new user account.

    Returns JWT tokens and user profile on success.
    """
    try:
        result = AuthService.register(
            email=body.email,
            full_name=body.full_name,
            password=body.password,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest):
    """
    Authenticate user with email and password.

    Returns JWT tokens and user profile on success.
    """
    try:
        result = AuthService.login(
            email=body.email,
            password=body.password,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(body: RefreshTokenRequest):
    """
    Refresh an expired access token using a valid refresh token.
    """
    try:
        result = AuthService.refresh_token(body.refresh_token)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout the current user.

    Note: With stateless JWTs, this is a client-side operation.
    The token remains valid until expiry. A token blacklist
    can be added later for immediate revocation.
    """
    return MessageResponse(
        message="Successfully logged out",
        success=True,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get the current authenticated user's profile.
    """
    return current_user
