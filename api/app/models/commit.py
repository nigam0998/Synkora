"""
Synkora API — Commit Record Model

Stores parsed Git commit history for a repository.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class CommitRecord(Base, UUIDMixin):
    """A single Git commit parsed from repository history."""

    __tablename__ = "commit_records"

    # Parent
    repository_id: Mapped[str] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Commit data
    sha: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    author_name: Mapped[str] = mapped_column(String(255), nullable=False)
    author_email: Mapped[str] = mapped_column(String(255), nullable=False)
    authored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    committer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    committed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Change stats
    files_changed: Mapped[int] = mapped_column(Integer, default=0)
    insertions: Mapped[int] = mapped_column(Integer, default=0)
    deletions: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    repository = relationship("Repository", back_populates="commits")

    def __repr__(self) -> str:
        return f"<CommitRecord {self.sha[:7]} by {self.author_name}>"
