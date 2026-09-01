"""
Synkora API — AI Router

Endpoints for AI-powered code analysis features:
  - POST /{repo_id}/enrich: Enrich the latest analysis with AI refactoring advice (all high/critical)
  - POST /insight/{insight_id}/enrich: Enrich a single insight on demand
  - GET  /{repo_id}/summary: Generate an AI executive summary of repo health
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.analysis import Analysis
from app.models.insight import Insight
from app.models.repository import Repository
from app.schemas.tech_debt import TechDebtIssue
from app.services.ai_service import AIService
from app.core.logging import get_logger

logger = get_logger("ai_router")

router = APIRouter()


async def _get_repo_or_404(db: AsyncSession, repo_id: str, owner_id: str) -> Repository:
    """Fetch a repository owned by the authenticated user, or raise 404."""
    result = await db.execute(
        select(Repository).where(Repository.id == repo_id, Repository.owner_id == owner_id)
    )
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    return repo


@router.post("/{repo_id}/enrich")
async def enrich_insights(
    repo_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Use Gemini AI to enrich the latest analysis insights with
    actionable refactoring advice. Updates insight recommendations in-place.
    """
    await _get_repo_or_404(db, repo_id, current_user["id"])

    # Fetch latest completed analysis
    result = await db.execute(
        select(Analysis)
        .where(Analysis.repository_id == repo_id, Analysis.status == "completed")
        .order_by(Analysis.created_at.desc())
        .limit(1)
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No completed analysis found for this repository",
        )

    # Fetch high/critical insights that still have generic recommendations
    insight_result = await db.execute(
        select(Insight).where(
            Insight.analysis_id == analysis.id,
            Insight.severity.in_(["critical", "high"]),
        )
    )
    insights = insight_result.scalars().all()

    if not insights:
        return {
            "message": "No high-severity insights to enrich",
            "enriched_count": 0,
        }

    enriched_count = 0
    for insight in insights:
        # Convert DB Insight → TechDebtIssue for the AI service
        issue = TechDebtIssue(
            issue_id=insight.id,
            rule_name=insight.title.split(" in ")[0] if " in " in insight.title else insight.title,
            description=insight.description,
            severity=insight.severity,
            file_path=insight.file_path or "unknown",
            start_line=insight.line_start,
            end_line=insight.line_end,
            related_metrics=insight.metadata_json or {},
        )

        advice = await AIService.enrich_insight(issue)

        # Persist the AI-generated recommendation back to the DB
        insight.recommendation = advice
        insight.confidence = 0.85  # Gemini-generated
        enriched_count += 1

    await db.commit()

    logger.info(
        "insights_enriched",
        repo_id=repo_id,
        analysis_id=analysis.id,
        enriched=enriched_count,
    )

    return {
        "message": f"Successfully enriched {enriched_count} insights with AI recommendations",
        "enriched_count": enriched_count,
        "analysis_id": analysis.id,
    }


@router.post("/insight/{insight_id}/enrich")
async def enrich_single_insight(
    insight_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Use Gemini AI to enrich a single specific insight with
    actionable refactoring advice on demand.
    """
    # Fetch insight
    result = await db.execute(select(Insight).where(Insight.id == insight_id))
    insight = result.scalar_one_or_none()
    if not insight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insight not found")

    # Authorize: ensure the user owns the repository the insight belongs to
    analysis_result = await db.execute(select(Analysis).where(Analysis.id == insight.analysis_id))
    analysis = analysis_result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
        
    await _get_repo_or_404(db, analysis.repository_id, current_user["id"])

    # Convert DB Insight → TechDebtIssue for the AI service
    issue = TechDebtIssue(
        issue_id=insight.id,
        rule_name=insight.title.split(" in ")[0] if " in " in insight.title else insight.title,
        description=insight.description,
        severity=insight.severity,
        file_path=insight.file_path or "unknown",
        start_line=insight.line_start,
        end_line=insight.line_end,
        related_metrics=insight.metadata_json or {},
    )

    advice = await AIService.enrich_insight(issue)

    # Persist the AI-generated recommendation back to the DB
    insight.recommendation = advice
    insight.confidence = 0.85  # Gemini-generated
    await db.commit()

    logger.info("single_insight_enriched", insight_id=insight.id)

    return {
        "message": "Successfully generated AI refactoring advice",
        "recommendation": advice,
    }



@router.get("/{repo_id}/summary")
async def get_repo_summary(
    repo_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate an AI-powered executive summary of the repository's health
    based on the latest completed analysis.
    """
    await _get_repo_or_404(db, repo_id, current_user["id"])

    # Fetch latest completed analysis
    result = await db.execute(
        select(Analysis)
        .where(Analysis.repository_id == repo_id, Analysis.status == "completed")
        .order_by(Analysis.created_at.desc())
        .limit(1)
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No completed analysis found for this repository",
        )

    # Count insights by severity
    insight_result = await db.execute(
        select(Insight).where(Insight.analysis_id == analysis.id)
    )
    insights = insight_result.scalars().all()
    severity_counts = {"critical": 0, "high": 0, "moderate": 0, "low": 0}
    for ins in insights:
        sev = ins.severity.lower()
        if sev in severity_counts:
            severity_counts[sev] += 1

    # Build a lightweight TechDebtReport for the AI service
    from app.schemas.tech_debt import TechDebtReport

    mock_report = TechDebtReport(
        total_issues=len(insights),
        critical_issues=severity_counts["critical"],
        high_issues=severity_counts["high"],
        moderate_issues=severity_counts["moderate"],
        low_issues=severity_counts["low"],
        total_remediation_minutes=int((analysis.tech_debt_score or 0) * 60),
    )

    summary = await AIService.generate_repo_summary(
        total_files=analysis.total_files,
        total_lines=analysis.total_lines,
        total_functions=analysis.total_functions,
        total_classes=analysis.total_classes,
        avg_complexity=analysis.avg_complexity or 0,
        tech_debt_report=mock_report,
    )

    return {
        "summary": summary,
        "analysis_id": analysis.id,
        "debt_grade": mock_report.debt_grade,
    }
