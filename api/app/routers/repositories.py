"""
Synkora API — Repositories Router

Full CRUD endpoints for managing connected repositories.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.repository import (
    RepositoryCreate,
    RepositoryResponse,
    RepositoryListResponse,
)
from app.schemas.auth import MessageResponse
from app.services.repo_service import RepositoryService
from app.services.github_service import GitHubService
from app.core.dependencies import get_current_user
from app.core.database import get_db

router = APIRouter()


@router.get("/", response_model=RepositoryListResponse)
async def list_repositories(
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all connected repositories for the authenticated user."""
    repos, total = await RepositoryService.list_by_owner(
        db=db,
        owner_id=current_user["id"],
        page=page,
        per_page=per_page,
    )
    return RepositoryListResponse(
        repositories=[RepositoryResponse.model_validate(r) for r in repos],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.post("/import", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
async def import_repository(
    body: RepositoryCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Connect a GitHub repository to Synkora for analysis.

    The frontend should first fetch the repo details from GitHub
    and then submit them to this endpoint.
    """
    try:
        repo = await RepositoryService.create(
            db=db,
            owner_id=current_user["id"],
            repo_data=body.model_dump(),
        )
        return RepositoryResponse.model_validate(repo)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/{repo_id}", response_model=RepositoryResponse)
async def get_repository(
    repo_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get details of a specific connected repository."""
    repo = await RepositoryService.get_by_id(
        db=db,
        repo_id=repo_id,
        owner_id=current_user["id"],
    )
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )
    return RepositoryResponse.model_validate(repo)


@router.delete("/{repo_id}", response_model=MessageResponse)
async def delete_repository(
    repo_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a repository from Synkora."""
    deleted = await RepositoryService.delete(
        db=db,
        repo_id=repo_id,
        owner_id=current_user["id"],
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )
    return MessageResponse(message="Repository removed successfully", success=True)


@router.post("/{repo_id}/analyze", response_model=MessageResponse)
async def trigger_analysis(
    repo_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger a new analysis run for a repository.

    This is a placeholder — full implementation comes with the
    analysis engine in Week 2.
    """
    repo = await RepositoryService.get_by_id(
        db=db,
        repo_id=repo_id,
        owner_id=current_user["id"],
    )
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )

    # Update status to queued
    await RepositoryService.update_status(db, repo_id, "analyzing")

    return MessageResponse(
        message=f"Analysis queued for {repo.full_name}",
        success=True,
    )
