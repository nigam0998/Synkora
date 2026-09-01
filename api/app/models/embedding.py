"""
Synkora API — Code Embedding Model

Stores vector embeddings for chunks of code (functions, classes, etc.)
to enable semantic code search and context-aware AI interactions.
"""

from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.models.base import Base, UUIDMixin, TimestampMixin


class CodeEmbedding(Base, UUIDMixin, TimestampMixin):
    """
    Represents a vectorized chunk of code from a repository.

    Each record stores a code snippet (function, class, or file chunk),
    its source location, and a dense vector embedding for similarity search.
    """
    __tablename__ = "code_embeddings"

    repository_id: Mapped[str] = mapped_column(
        String, ForeignKey("repositories.id", ondelete="CASCADE"), index=True, nullable=False
    )
    analysis_id: Mapped[str] = mapped_column(
        String, ForeignKey("analyses.id", ondelete="CASCADE"), index=True, nullable=False
    )

    file_path: Mapped[str] = mapped_column(String, index=True, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    line_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    line_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # 384 dimensions — matches all-MiniLM-L6-v2 output
    embedding = mapped_column(Vector(384), nullable=False)

    # Relationships
    repository = relationship("Repository", backref="embeddings")
    analysis = relationship("Analysis", backref="embeddings")
