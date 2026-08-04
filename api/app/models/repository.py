"""
Synkora API — Repository Model

Represents a GitHub repository connected for analysis.
"""

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Repository(Base, UUIDMixin, TimestampMixin):
    """A GitHub repository connected to Synkora for analysis."""

    __tablename__ = "repositories"
    __table_args__ = (
        UniqueConstraint("owner_id", "github_repo_id", name="uq_repo_owner_github"),
    )

    # Owner
    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # GitHub metadata
    github_repo_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(500), nullable=False)  # e.g. "owner/repo"
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    html_url: Mapped[str] = mapped_column(Text, nullable=False)
    clone_url: Mapped[str] = mapped_column(Text, nullable=False)
    default_branch: Mapped[str] = mapped_column(String(100), default="main")
    language: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)

    # Stats (cached from GitHub)
    stars_count: Mapped[int] = mapped_column(Integer, default=0)
    forks_count: Mapped[int] = mapped_column(Integer, default=0)
    open_issues_count: Mapped[int] = mapped_column(Integer, default=0)
    size_kb: Mapped[int] = mapped_column(Integer, default=0)

    # Analysis status
    analysis_status: Mapped[str] = mapped_column(
        String(50), default="pending"
    )  # pending | cloning | analyzing | ready | error
    last_analyzed_commit: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)

    # Local storage
    local_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="repositories")
    analyses = relationship("Analysis", back_populates="repository", cascade="all, delete-orphan")
    commits = relationship("CommitRecord", back_populates="repository", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Repository {self.full_name}>"
