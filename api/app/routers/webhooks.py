"""
Synkora API — Webhook Router

Handles incoming GitHub webhook events.
Currently supports:
  - push: Triggers a re-analysis when code is pushed to the default branch.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.webhook_verify import verify_github_signature
from app.core.task_manager import submit_task
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.repository import Repository
from app.services.clone_service import CloneService
from app.services.repo_service import RepositoryService
from app.schemas.webhook import WebhookResponse

logger = get_logger("webhook_router")

router = APIRouter()


@router.post("/github", response_model=WebhookResponse)
async def github_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Receive and process GitHub webhook events.

    GitHub sends various events (push, pull_request, etc.).
    We currently handle:
      - push: Re-clone + re-analyze when code is pushed to the default branch.
    """
    # ── 1. Read raw body and verify signature ────────────────
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    delivery_id = request.headers.get("X-GitHub-Delivery", "unknown")

    # Signature verification (skip if no webhook secret is configured)
    if not verify_github_signature(body, signature):
        logger.warning(
            "webhook_signature_invalid",
            event=event_type,
            delivery_id=delivery_id,
        )
        # In development, we allow unsigned webhooks
        # In production, uncomment the following:
        # raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")

    logger.info(
        "webhook_received",
        event=event_type,
        delivery_id=delivery_id,
    )

    # ── 2. Parse event ───────────────────────────────────────
    payload = await request.json()

    if event_type == "ping":
        return WebhookResponse(
            status="accepted",
            message=f"Pong! Webhook configured for {payload.get('repository', {}).get('full_name', 'unknown')}",
        )

    if event_type == "push":
        return await _handle_push_event(payload, db)

    # Ignore other events gracefully
    return WebhookResponse(
        status="ignored",
        message=f"Event type '{event_type}' is not handled",
    )


async def _handle_push_event(payload: dict, db: AsyncSession) -> WebhookResponse:
    """
    Handle a GitHub push event.

    When code is pushed to the default branch of a connected repo,
    we trigger a pull + re-analysis.
    """
    repo_data = payload.get("repository", {})
    github_repo_id = repo_data.get("id")
    ref = payload.get("ref", "")
    default_branch = repo_data.get("default_branch", "main")

    # Only process pushes to the default branch
    if ref != f"refs/heads/{default_branch}":
        return WebhookResponse(
            status="ignored",
            message=f"Push to non-default branch ({ref}) — skipped",
        )

    # Find the connected repository
    stmt = select(Repository).where(Repository.github_repo_id == github_repo_id)
    result = await db.execute(stmt)
    repo = result.scalar_one_or_none()

    if not repo:
        return WebhookResponse(
            status="ignored",
            message=f"Repository {repo_data.get('full_name', github_repo_id)} is not connected to Synkora",
        )

    # Update status
    await RepositoryService.update_status(db, repo.id, "analyzing")

    # Submit background task for clone/pull + analysis
    after_sha = payload.get("after", "")
    task_status = await submit_task(
        name=f"Webhook sync: {repo.full_name}",
        coro_fn=_sync_and_analyze,
        repo_id=repo.id,
        repo_full_name=repo.full_name,
        clone_url=repo.clone_url,
        branch=default_branch,
        commit_sha=after_sha,
    )

    logger.info(
        "push_event_processed",
        repo=repo.full_name,
        commit=after_sha[:7] if after_sha else "unknown",
        task_id=task_status.task_id,
    )

    return WebhookResponse(
        status="accepted",
        message=f"Push to {repo.full_name} accepted — analysis queued",
        task_id=task_status.task_id,
    )


async def _sync_and_analyze(
    task_status,
    repo_id: str,
    repo_full_name: str,
    clone_url: str,
    branch: str,
    commit_sha: str,
):
    """
    Background task: sync repository and trigger analysis.

    Steps:
      1. Pull latest (or clone if not yet cloned)
      2. Update repo status and last_analyzed_commit
      3. Trigger analysis (placeholder for Week 2)
    """
    from app.core.database import async_session_factory

    try:
        # Step 1: Pull or clone
        clone_info = CloneService.get_clone_info(repo_full_name)
        if clone_info:
            task_status.message = f"Pulling latest for {repo_full_name}..."
            task_status.progress = 20.0
            await CloneService.pull_latest(repo_full_name, branch)
        else:
            task_status.message = f"Cloning {repo_full_name}..."
            task_status.progress = 10.0
            await CloneService.clone_repo(
                task_status, clone_url, repo_full_name, branch
            )

        # Step 2: Update DB
        task_status.message = "Updating repository status..."
        task_status.progress = 70.0

        async with async_session_factory() as db:
            await RepositoryService.update_status(
                db, repo_id, "ready", last_commit=commit_sha
            )
            await db.commit()

        # Step 3: Analysis (placeholder)
        task_status.message = "Analysis will be triggered in Week 2"
        task_status.progress = 100.0

        return {"commit_sha": commit_sha, "status": "ready"}

    except Exception as e:
        # Update status to error
        async with async_session_factory() as db:
            await RepositoryService.update_status(db, repo_id, "error")
            await db.commit()
        raise
