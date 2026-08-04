"""
Synkora API — Repository Schemas

Pydantic models for repository request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RepositoryCreate(BaseModel):
    """Schema for connecting a new repository."""

    github_repo_id: int
    name: str = Field(..., max_length=255)
    full_name: str = Field(..., max_length=500)
    description: Optional[str] = None
    html_url: str
    clone_url: str
    default_branch: str = "main"
    language: Optional[str] = None
    is_private: bool = False
    stars_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    size_kb: int = 0


class RepositoryResponse(BaseModel):
    """Schema for repository data in responses."""

    id: str
    owner_id: str
    github_repo_id: int
    name: str
    full_name: str
    description: Optional[str] = None
    html_url: str
    clone_url: str
    default_branch: str
    language: Optional[str] = None
    is_private: bool
    stars_count: int
    forks_count: int
    open_issues_count: int
    size_kb: int
    analysis_status: str
    last_analyzed_commit: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RepositoryListResponse(BaseModel):
    """Paginated list of repositories."""

    repositories: list[RepositoryResponse]
    total: int
    page: int
    per_page: int
