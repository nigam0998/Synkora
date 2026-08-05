"""
Synkora API — Repository Service

Business logic for managing connected repositories (CRUD operations).
"""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.repository import Repository
from app.core.logging import get_logger

logger = get_logger("repo_service")


class RepositoryService:
    """Service for repository CRUD operations."""

    @staticmethod
    async def create(
        db: AsyncSession,
        owner_id: str,
        repo_data: dict,
    ) -> Repository:
        """
        Connect a GitHub repository to Synkora.

        Checks for duplicates (same owner + github_repo_id) before creating.
        """
        # Check for existing
        stmt = select(Repository).where(
            Repository.owner_id == owner_id,
            Repository.github_repo_id == repo_data["github_repo_id"],
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise ValueError(f"Repository '{repo_data['full_name']}' is already connected")

        repo = Repository(owner_id=owner_id, **repo_data)
        db.add(repo)
        await db.flush()
        await db.refresh(repo)

        logger.info("repository_connected", repo_id=repo.id, full_name=repo.full_name)
        return repo

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        repo_id: str,
        owner_id: Optional[str] = None,
    ) -> Optional[Repository]:
        """Get a repository by ID, optionally scoped to an owner."""
        stmt = select(Repository).where(Repository.id == repo_id)
        if owner_id:
            stmt = stmt.where(Repository.owner_id == owner_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_owner(
        db: AsyncSession,
        owner_id: str,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Repository], int]:
        """
        List all repositories for a specific owner with pagination.

        Returns: (repositories, total_count)
        """
        # Count
        count_stmt = select(func.count()).select_from(Repository).where(
            Repository.owner_id == owner_id
        )
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Fetch page
        stmt = (
            select(Repository)
            .where(Repository.owner_id == owner_id)
            .order_by(Repository.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await db.execute(stmt)
        repos = list(result.scalars().all())

        return repos, total

    @staticmethod
    async def update_status(
        db: AsyncSession,
        repo_id: str,
        status: str,
        last_commit: Optional[str] = None,
    ) -> Optional[Repository]:
        """Update the analysis status of a repository."""
        stmt = select(Repository).where(Repository.id == repo_id)
        result = await db.execute(stmt)
        repo = result.scalar_one_or_none()

        if not repo:
            return None

        repo.analysis_status = status
        if last_commit:
            repo.last_analyzed_commit = last_commit

        await db.flush()
        await db.refresh(repo)
        return repo

    @staticmethod
    async def delete(
        db: AsyncSession,
        repo_id: str,
        owner_id: str,
    ) -> bool:
        """Delete a repository. Returns True if deleted, False if not found."""
        stmt = select(Repository).where(
            Repository.id == repo_id,
            Repository.owner_id == owner_id,
        )
        result = await db.execute(stmt)
        repo = result.scalar_one_or_none()

        if not repo:
            return False

        await db.delete(repo)
        await db.flush()

        logger.info("repository_deleted", repo_id=repo_id)
        return True
