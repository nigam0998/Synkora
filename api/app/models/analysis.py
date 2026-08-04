"""
Synkora API — Analysis Model

Represents a code analysis run on a repository.
"""

from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Analysis(Base, UUIDMixin, TimestampMixin):
    """A code analysis run for a specific repository snapshot."""

    __tablename__ = "analyses"

    # Parent
    repository_id: Mapped[str] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Analysis metadata
    commit_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    branch: Mapped[str] = mapped_column(String(255), default="main")
    status: Mapped[str] = mapped_column(
        String(50), default="queued"
    )  # queued | running | completed | failed

    # Metrics (summary)
    total_files: Mapped[int] = mapped_column(Integer, default=0)
    total_lines: Mapped[int] = mapped_column(Integer, default=0)
    total_functions: Mapped[int] = mapped_column(Integer, default=0)
    total_classes: Mapped[int] = mapped_column(Integer, default=0)
    avg_complexity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tech_debt_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bug_risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Language breakdown — stored as JSON: {"Python": 45.2, "TypeScript": 30.1, ...}
    language_breakdown: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Dependency data — stored as JSON
    dependencies: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Error info (if status == "failed")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    repository = relationship("Repository", back_populates="analyses")
    insights = relationship("Insight", back_populates="analysis", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Analysis {self.repository_id}:{self.commit_sha[:7]}>"
