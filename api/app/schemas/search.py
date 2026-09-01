"""
Synkora API — Search Schemas

Request/response models for the Semantic Code Search endpoint.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request body for semantic code search."""
    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural-language query describing what you are looking for.",
        examples=["authentication middleware", "database connection pool"],
    )
    repository_id: str = Field(
        ...,
        description="ID of the repository to search within.",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of results to return.",
    )
    content_type: Optional[str] = Field(
        default=None,
        description="Filter by content type: 'function', 'class', or 'file'.",
    )
    min_score: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Minimum cosine similarity score (0–1). Lower values return more results.",
    )


class SearchResult(BaseModel):
    """A single semantic search result."""
    file_path: str = Field(description="Relative file path within the repository.")
    content_type: str = Field(description="Type of matched code chunk.")
    content: str = Field(description="The matched code snippet.")
    line_start: Optional[int] = Field(default=None, description="Starting line number.")
    line_end: Optional[int] = Field(default=None, description="Ending line number.")
    score: float = Field(description="Cosine similarity score (0–1, higher is better).")


class SearchResponse(BaseModel):
    """Response body for semantic code search."""
    query: str = Field(description="The original search query.")
    repository_id: str
    total_results: int
    results: List[SearchResult]
