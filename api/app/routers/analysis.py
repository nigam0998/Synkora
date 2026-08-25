"""
Synkora API — Analysis Router (Stub)

Placeholder endpoints for code analysis features. Full implementation in Week 2.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.analysis import Analysis
from app.models.insight import Insight
from app.models.repository import Repository
from app.schemas.analysis import AnalysisDetailResponse, AnalysisHistoryResponse, AnalysisResponse, InsightResponse

router = APIRouter()


async def get_repo_or_404(db: AsyncSession, repo_id: str, owner_id: str) -> Repository:
    result = await db.execute(
        select(Repository).where(Repository.id == repo_id, Repository.owner_id == owner_id)
    )
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    return repo


@router.get("/{repo_id}/latest", response_model=AnalysisDetailResponse)
async def get_latest_analysis(
    repo_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the most recent analysis run for a repository, including insights."""
    await get_repo_or_404(db, repo_id, current_user["id"])

    # Fetch latest completed analysis
    result = await db.execute(
        select(Analysis)
        .where(Analysis.repository_id == repo_id, Analysis.status == "completed")
        .order_by(Analysis.created_at.desc())
        .limit(1)
    )
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No completed analysis found")

    # Fetch insights
    insight_result = await db.execute(
        select(Insight).where(Insight.analysis_id == analysis.id)
    )
    insights = insight_result.scalars().all()

    # Calculate insight summary
    summary = {"critical": 0, "high": 0, "moderate": 0, "low": 0}
    for ins in insights:
        sev = ins.severity.lower()
        if sev in summary:
            summary[sev] += 1

    return AnalysisDetailResponse(
        analysis=AnalysisResponse.model_validate(analysis),
        insights=[InsightResponse.model_validate(ins) for ins in insights],
        insight_summary=summary,
    )


@router.get("/{repo_id}/history", response_model=AnalysisHistoryResponse)
async def get_analysis_history(
    repo_id: str,
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the history of analysis runs for trend charting."""
    await get_repo_or_404(db, repo_id, current_user["id"])

    result = await db.execute(
        select(Analysis)
        .where(Analysis.repository_id == repo_id, Analysis.status == "completed")
        .order_by(Analysis.created_at.desc())
        .limit(limit)
    )
    analyses = result.scalars().all()
    # Return chronologically (oldest first for charts)
    analyses.reverse()

    return AnalysisHistoryResponse(
        history=[AnalysisResponse.model_validate(a) for a in analyses]
    )
