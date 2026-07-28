"""
Synkora API — Analysis Router (Stub)

Placeholder endpoints for code analysis features. Full implementation in Week 2.
"""

from fastapi import APIRouter

router = APIRouter()


@router.post("/{repo_id}/run")
async def run_analysis(repo_id: str):
    """Trigger a full analysis run on a repository."""
    return {"message": f"Analysis for {repo_id} — coming Week 2"}


@router.get("/{repo_id}/status")
async def analysis_status(repo_id: str):
    """Check the status of an ongoing analysis."""
    return {"message": f"Analysis status for {repo_id} — coming Week 2"}


@router.get("/{repo_id}/metrics")
async def get_metrics(repo_id: str):
    """Get code metrics for a repository."""
    return {"message": f"Metrics for {repo_id} — coming Week 2"}


@router.get("/{repo_id}/dependencies")
async def get_dependencies(repo_id: str):
    """Get dependency graph for a repository."""
    return {"message": f"Dependencies for {repo_id} — coming Week 2"}


@router.get("/{repo_id}/evolution")
async def get_evolution(repo_id: str):
    """Get code evolution timeline for a repository."""
    return {"message": f"Evolution timeline for {repo_id} — coming Week 2"}


@router.get("/{repo_id}/tech-debt")
async def get_tech_debt(repo_id: str):
    """Get technical debt report for a repository."""
    return {"message": f"Tech debt for {repo_id} — coming Week 2"}
