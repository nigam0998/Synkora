"""
Synkora API — User Model

SQLAlchemy ORM model for the users table.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """User account model."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # GitHub OAuth
    github_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    github_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    github_access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    repositories = relationship("Repository", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.email}>"
