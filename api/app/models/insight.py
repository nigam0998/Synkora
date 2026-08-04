"""
Synkora API — Insight Model

Stores AI-generated insights and detected issues from analysis.
"""

from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Insight(Base, UUIDMixin, TimestampMixin):
    """An AI-generated insight or detected issue from code analysis."""

    __tablename__ = "insights"

    # Parent
    analysis_id: Mapped[str] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Insight classification
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # architecture | tech_debt | bug_risk | security | performance | documentation

    severity: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # critical | high | medium | low | info

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Location
    file_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    line_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    line_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Scoring
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0.0 - 1.0
    impact_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0.0 - 10.0

    # Additional structured data
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Status
    is_resolved: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    analysis = relationship("Analysis", back_populates="insights")

    def __repr__(self) -> str:
        return f"<Insight [{self.severity}] {self.title[:40]}>"
