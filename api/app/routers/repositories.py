"""
Synkora API — Repositories Router (Stub)

Placeholder endpoints for repository management. Full implementation on Days 6-7.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_repositories():
    """List all repositories for the authenticated user."""
    return {"message": "Repository listing — coming Days 6-7", "repositories": []}


@router.post("/import")
async def import_repository():
    """Import a GitHub repository for analysis."""
    return {"message": "Repository import — coming Days 6-7"}


@router.get("/{repo_id}")
async def get_repository(repo_id: str):
    """Get details of a specific repository."""
    return {"message": f"Repository {repo_id} details — coming Days 6-7"}


@router.delete("/{repo_id}")
async def delete_repository(repo_id: str):
    """Remove a repository from Synkora."""
    return {"message": f"Repository {repo_id} deletion — coming Days 6-7"}
