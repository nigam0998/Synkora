"""
Synkora API — Auth Service

Business logic for user authentication — register, login, token refresh.
Uses an in-memory user store for development (will switch to PostgreSQL on Day 4).
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from app.core.security import (
    create_token_pair,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.logging import get_logger

logger = get_logger("auth_service")

# ── In-Memory User Store (temporary until Day 4 DB integration) ──────────
# Keyed by user ID (str), value is a dict representing the user record.
_users_db: dict[str, dict] = {}
_email_index: dict[str, str] = {}  # email -> user_id for quick lookup


class AuthService:
    """Handles user authentication operations."""

    @staticmethod
    def register(email: str, full_name: str, password: str) -> dict:
        """
        Register a new user account.

        Raises:
            ValueError: If email is already registered.

        Returns:
            Dict with 'tokens' and 'user' keys.
        """
        # Check for duplicate email
        if email.lower() in _email_index:
            raise ValueError("A user with this email already exists")

        # Create user record
        user_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        user = {
            "id": user_id,
            "email": email.lower(),
            "full_name": full_name,
            "hashed_password": hash_password(password),
            "avatar_url": None,
            "github_id": None,
            "github_username": None,
            "github_connected": False,
            "is_active": True,
            "is_verified": False,
            "created_at": now,
            "updated_at": now,
            "last_login_at": now,
        }

        _users_db[user_id] = user
        _email_index[email.lower()] = user_id

        logger.info("user_registered", user_id=user_id, email=email)

        # Generate tokens
        tokens = create_token_pair(user_id)

        return {
            "tokens": tokens,
            "user": _sanitize_user(user),
        }

    @staticmethod
    def login(email: str, password: str) -> dict:
        """
        Authenticate a user with email and password.

        Raises:
            ValueError: If credentials are invalid.

        Returns:
            Dict with 'tokens' and 'user' keys.
        """
        user_id = _email_index.get(email.lower())
        if not user_id:
            raise ValueError("Invalid email or password")

        user = _users_db.get(user_id)
        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(password, user["hashed_password"]):
            raise ValueError("Invalid email or password")

        if not user["is_active"]:
            raise ValueError("Account has been deactivated")

        # Update last login
        user["last_login_at"] = datetime.now(timezone.utc)

        logger.info("user_logged_in", user_id=user_id)

        tokens = create_token_pair(user_id)

        return {
            "tokens": tokens,
            "user": _sanitize_user(user),
        }

    @staticmethod
    def refresh_token(refresh_token_str: str) -> dict:
        """
        Generate a new access token using a valid refresh token.

        Raises:
            ValueError: If the refresh token is invalid or expired.

        Returns:
            Dict with new token pair.
        """
        payload = decode_token(refresh_token_str)
        if not payload:
            raise ValueError("Invalid or expired refresh token")

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type — expected refresh token")

        user_id = payload.get("sub")
        user = _users_db.get(user_id) if user_id else None

        if not user:
            raise ValueError("User not found")

        if not user["is_active"]:
            raise ValueError("Account has been deactivated")

        logger.info("token_refreshed", user_id=user_id)

        tokens = create_token_pair(user_id)

        return {
            "tokens": tokens,
            "user": _sanitize_user(user),
        }

    @staticmethod
    def get_current_user(token: str) -> Optional[dict]:
        """
        Validate an access token and return the associated user.

        Returns:
            Sanitized user dict, or None if token is invalid.
        """
        payload = decode_token(token)
        if not payload:
            return None

        if payload.get("type") != "access":
            return None

        user_id = payload.get("sub")
        user = _users_db.get(user_id) if user_id else None

        if not user or not user["is_active"]:
            return None

        return _sanitize_user(user)


def _sanitize_user(user: dict) -> dict:
    """Remove sensitive fields from user dict for API responses."""
    return {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "avatar_url": user["avatar_url"],
        "github_connected": bool(user.get("github_id")),
        "is_active": user["is_active"],
        "is_verified": user["is_verified"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
    }
