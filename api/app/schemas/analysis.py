"""
Synkora API — Analysis Schemas

Pydantic models for analysis request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AnalysisResponse(BaseModel):
    """Schema for analysis data in responses."""

    id: str
    repository_id: str
    commit_sha: str
    branch: str
    status: str
    total_files: int
    total_lines: int
    total_functions: int
    total_classes: int
    avg_complexity: Optional[float] = None
    tech_debt_score: Optional[float] = None
    bug_risk_score: Optional[float] = None
    language_breakdown: Optional[dict] = None
    dependencies: Optional[dict] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InsightResponse(BaseModel):
    """Schema for insight data in responses."""

    id: str
    analysis_id: str
    category: str
    severity: str
    title: str
    description: str
    recommendation: Optional[str] = None
    file_path: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    confidence: Optional[float] = None
    impact_score: Optional[float] = None
    is_resolved: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisDetailResponse(BaseModel):
    """Analysis with its insights."""

    analysis: AnalysisResponse
    insights: list[InsightResponse]
    insight_summary: dict  # { "critical": 2, "high": 5, ... }
