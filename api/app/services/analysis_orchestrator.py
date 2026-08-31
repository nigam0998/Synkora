"""
Synkora API — Analysis Orchestrator Service

Master pipeline that orchestrates the entire code analysis process.
Invoked by webhook events, runs asynchronously in the background.
Coordinates Cloning, AST Parsing, Metrics, Dependencies, Git History,
and Tech Debt detection, then persists results to PostgreSQL.
"""

import traceback
from typing import Optional
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.logging import get_logger
from app.core.config import settings
from app.models.repository import Repository
from app.models.analysis import Analysis
from app.models.insight import Insight
from app.models.commit import CommitRecord

from app.services.clone_service import CloneService
from app.services.ast_service import ASTService
from app.services.metrics_service import MetricsService
from app.services.dependency_service import DependencyService
from app.services.git_history_service import GitHistoryService
from app.services.tech_debt_service import TechDebtService

logger = get_logger("analysis_orchestrator")


class AnalysisOrchestrator:
    """Master service for orchestrating full-repository code analysis."""

    @staticmethod
    async def run_pipeline(
        task_status,
        db: AsyncSession,
        repository_id: str,
        commit_sha: str,
        branch: str = "main",
    ) -> None:
        """
        Execute the full analysis pipeline for a specific repository and commit.
        This is intended to be run as a background task.
        """
        # 1. Fetch Repository and Setup Analysis Record
        result = await db.execute(select(Repository).where(Repository.id == repository_id))
        repo = result.scalar_one_or_none()
        
        if not repo:
            logger.error("repo_not_found", repo_id=repository_id)
            return

        # Mark repo as analyzing
        repo.analysis_status = "analyzing"
        
        # Create Analysis snapshot record
        analysis = Analysis(
            repository_id=repo.id,
            commit_sha=commit_sha,
            branch=branch,
            status="running"
        )
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)

        logger.info("pipeline_started", repo=repo.full_name, commit=commit_sha, analysis_id=analysis.id)

        try:
            # 2. Clone / Pull Repository
            task_status.message = f"Preparing repository {repo.full_name}..."
            task_status.progress = 10.0
            
            clone_info = CloneService.get_clone_info(repo.full_name)
            if clone_info:
                task_status.message = f"Pulling latest code..."
                task_status.progress = 20.0
                await CloneService.pull_latest(repo.full_name, branch)
                repo_path = Path(clone_info["path"])
            else:
                task_status.message = f"Cloning repository..."
                task_status.progress = 10.0
                clone_result = await CloneService.clone_repo(
                    task_status=task_status,
                    clone_url=repo.clone_url,
                    repo_full_name=repo.full_name,
                    branch=branch
                )
                repo_path = Path(clone_result["path"])
                
            # If repo_path wasn't saved to DB yet, save it
            if not repo.local_path:
                repo.local_path = str(repo_path)
                await db.commit()

            # 3. Execute Analysis Engines
            task_status.message = "Running code metrics engine..."
            task_status.progress = 40.0
            metrics = MetricsService.analyze_repository(repo_path)
            
            logger.info("running_dependency_engine", repo=repo.full_name)
            task_status.message = "Running dependency analysis..."
            task_status.progress = 60.0
            dependencies = DependencyService.build_graph(repo_path)
            
            logger.info("running_git_history_engine", repo=repo.full_name)
            task_status.message = "Running git history analysis..."
            task_status.progress = 80.0
            history = await GitHistoryService.analyze_repository(repo_path, max_commits=500, branch=branch)
            
            logger.info("running_tech_debt_engine", repo=repo.full_name)
            task_status.message = "Running tech debt analysis..."
            task_status.progress = 90.0
            tech_debt = TechDebtService.analyze_repository(
                metrics=metrics,
                dependencies=dependencies,
                history=history
            )

            # 4. Persist Results to PostgreSQL

            # Update Analysis Record
            analysis.total_files = metrics.total_files
            analysis.total_lines = metrics.total_lines
            analysis.total_functions = metrics.total_functions
            analysis.total_classes = metrics.total_classes
            analysis.avg_complexity = metrics.avg_complexity
            analysis.tech_debt_score = tech_debt.total_remediation_hours
            analysis.language_breakdown = metrics.language_breakdown
            
            # Save dependency metrics as JSON
            analysis.dependencies = {
                "total_edges": dependencies.total_edges,
                "avg_coupling": dependencies.avg_out_degree,
                "circular_deps_count": dependencies.circular_dep_count,
            }

            # Map Tech Debt Issues to Insights
            for issue in tech_debt.issues:
                insight = Insight(
                    analysis_id=analysis.id,
                    category="tech_debt",
                    severity=issue.severity,
                    title=f"{issue.rule_name} in {Path(issue.file_path).name}",
                    description=issue.description,
                    recommendation=f"Estimated remediation: {issue.estimated_remediation_minutes} minutes.",
                    file_path=issue.file_path,
                    line_start=issue.start_line,
                    line_end=issue.end_line,
                    impact_score=issue.estimated_remediation_minutes / 60.0,
                    metadata_json=issue.related_metrics
                )
                db.add(insight)

            # Save Commit History
            # First clear old commits for this repo to avoid duplicates (simplest approach for now)
            await db.execute(delete(CommitRecord).where(CommitRecord.repository_id == repo.id))
            
            for commit in history.commits:
                commit_record = CommitRecord(
                    repository_id=repo.id,
                    sha=commit.sha,
                    message=commit.message,
                    author_name=commit.author_name,
                    author_email=commit.author_email,
                    authored_at=commit.authored_at,
                    files_changed=commit.files_changed,
                    insertions=commit.insertions,
                    deletions=commit.deletions,
                )
                db.add(commit_record)

            # Mark as completed
            analysis.status = "completed"
            repo.analysis_status = "ready"
            repo.last_analyzed_commit = commit_sha
            
            await db.commit()
            logger.info("pipeline_completed", repo=repo.full_name, analysis_id=analysis.id)

            # 5. AI Enrichment (best-effort, does not block pipeline)
            try:
                from app.services.ai_service import AIService
                from app.core.config import settings

                if settings.GEMINI_API_KEY:
                    task_status.message = "Enriching insights with AI..."
                    task_status.progress = 95.0

                    enrichments = await AIService.enrich_all_insights(tech_debt)

                    # Persist AI recommendations back to the insight rows
                    if enrichments:
                        insight_result = await db.execute(
                            select(Insight).where(Insight.analysis_id == analysis.id)
                        )
                        db_insights = insight_result.scalars().all()
                        for db_insight in db_insights:
                            # Match by title prefix (rule_name)
                            for issue_id, advice in enrichments.items():
                                if db_insight.id == issue_id or (
                                    db_insight.metadata_json
                                    and db_insight.metadata_json == next(
                                        (i.related_metrics for i in tech_debt.issues if i.issue_id == issue_id), None
                                    )
                                ):
                                    db_insight.recommendation = advice
                                    db_insight.confidence = 0.85
                                    break

                        await db.commit()
                        logger.info("ai_enrichment_completed", enriched=len(enrichments))
                else:
                    logger.info("ai_enrichment_skipped", reason="GEMINI_API_KEY not configured")

            except Exception as ai_err:
                # AI enrichment is non-critical — log and continue
                logger.warning("ai_enrichment_failed", error=str(ai_err))

        except Exception as e:
            # Handle Failures
            error_trace = traceback.format_exc()
            logger.error("pipeline_failed", repo=repo.full_name, error=str(e), trace=error_trace)
            
            analysis.status = "failed"
            analysis.error_message = str(e)
            repo.analysis_status = "error"
            
            await db.commit()

