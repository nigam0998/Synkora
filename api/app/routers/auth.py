"""
Synkora API — Authentication Router (Stub)

Placeholder endpoints for authentication. Full implementation on Day 3.
"""

from fastapi import APIRouter

router = APIRouter()


@router.post("/register")
async def register():
    """Register a new user account."""
    return {"message": "Registration endpoint — coming Day 3"}


@router.post("/login")
async def login():
    """Authenticate user and return JWT tokens."""
    return {"message": "Login endpoint — coming Day 3"}


@router.post("/refresh")
async def refresh_token():
    """Refresh an expired access token."""
    return {"message": "Token refresh endpoint — coming Day 3"}


@router.post("/logout")
async def logout():
    """Invalidate the current session."""
    return {"message": "Logout endpoint — coming Day 3"}
