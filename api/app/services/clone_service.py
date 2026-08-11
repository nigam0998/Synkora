"""
Synkora API — Repository Cloning Service

Handles cloning GitHub repositories to local storage for analysis.
Uses GitPython for Git operations.
"""

import shutil
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger
from app.core.task_manager import TaskStatus

logger = get_logger("clone_service")


class CloneService:
    """Service for cloning and managing local repository copies."""

    @staticmethod
    def get_repo_path(repo_full_name: str) -> Path:
        """Get the local storage path for a repository."""
        safe_name = repo_full_name.replace("/", "_")
        return Path(settings.REPO_STORAGE_PATH) / safe_name

    @staticmethod
    async def clone_repo(
        task_status: TaskStatus,
        clone_url: str,
        repo_full_name: str,
        branch: str = "main",
        access_token: str | None = None,
    ) -> dict:
        """
        Clone a GitHub repository to local storage.

        This is designed to run as a background task via the task manager.

        Args:
            task_status: TaskStatus object for progress reporting.
            clone_url: HTTPS clone URL of the repository.
            repo_full_name: e.g. "owner/repo-name"
            branch: Branch to clone.
            access_token: GitHub token for private repos.

        Returns:
            Dict with clone results.
        """
        import asyncio
        from git import Repo, GitCommandError

        repo_path = CloneService.get_repo_path(repo_full_name)

        task_status.message = f"Preparing to clone {repo_full_name}..."
        task_status.progress = 5.0

        # If directory exists, remove it for a fresh clone
        if repo_path.exists():
            task_status.message = "Cleaning up previous clone..."
            task_status.progress = 10.0
            shutil.rmtree(repo_path, ignore_errors=True)

        # Ensure parent directory exists
        repo_path.parent.mkdir(parents=True, exist_ok=True)

        # Inject token into clone URL for private repos
        authenticated_url = clone_url
        if access_token and clone_url.startswith("https://"):
            authenticated_url = clone_url.replace(
                "https://", f"https://x-access-token:{access_token}@"
            )

        task_status.message = f"Cloning {repo_full_name}..."
        task_status.progress = 20.0

        try:
            # Run the blocking Git clone in a thread
            def _do_clone():
                return Repo.clone_from(
                    authenticated_url,
                    str(repo_path),
                    branch=branch,
                    depth=100,  # Shallow clone for faster initial analysis
                    single_branch=True,
                )

            repo = await asyncio.to_thread(_do_clone)

            task_status.message = "Gathering repository statistics..."
            task_status.progress = 80.0

            # Gather basic stats
            def _get_stats():
                commit_count = sum(1 for _ in repo.iter_commits(max_count=100))
                file_count = sum(1 for _ in repo_path.rglob("*") if _.is_file() and ".git" not in str(_))
                total_size = sum(
                    f.stat().st_size
                    for f in repo_path.rglob("*")
                    if f.is_file() and ".git" not in str(f)
                )
                head_sha = str(repo.head.commit.hexsha)
                return {
                    "commit_count": commit_count,
                    "file_count": file_count,
                    "total_size_bytes": total_size,
                    "head_sha": head_sha,
                }

            stats = await asyncio.to_thread(_get_stats)

            task_status.message = "Clone completed successfully"
            task_status.progress = 100.0

            logger.info(
                "repo_cloned",
                repo=repo_full_name,
                path=str(repo_path),
                files=stats["file_count"],
                commits=stats["commit_count"],
            )

            return {
                "path": str(repo_path),
                "branch": branch,
                **stats,
            }

        except GitCommandError as e:
            logger.error("clone_failed", repo=repo_full_name, error=str(e))
            # Cleanup on failure
            if repo_path.exists():
                shutil.rmtree(repo_path, ignore_errors=True)
            raise RuntimeError(f"Failed to clone {repo_full_name}: {e.stderr or str(e)}")

    @staticmethod
    async def pull_latest(
        repo_full_name: str,
        branch: str = "main",
    ) -> dict:
        """Pull the latest changes for an already-cloned repository."""
        import asyncio
        from git import Repo, GitCommandError

        repo_path = CloneService.get_repo_path(repo_full_name)

        if not repo_path.exists():
            raise FileNotFoundError(f"Repository not found at {repo_path}")

        try:
            def _do_pull():
                repo = Repo(str(repo_path))
                origin = repo.remotes.origin
                origin.pull(branch)
                return str(repo.head.commit.hexsha)

            head_sha = await asyncio.to_thread(_do_pull)

            logger.info("repo_updated", repo=repo_full_name, head_sha=head_sha[:7])

            return {"head_sha": head_sha, "path": str(repo_path)}

        except GitCommandError as e:
            logger.error("pull_failed", repo=repo_full_name, error=str(e))
            raise RuntimeError(f"Failed to pull {repo_full_name}: {e.stderr or str(e)}")

    @staticmethod
    def delete_clone(repo_full_name: str) -> bool:
        """Delete the local clone of a repository."""
        repo_path = CloneService.get_repo_path(repo_full_name)
        if repo_path.exists():
            shutil.rmtree(repo_path, ignore_errors=True)
            logger.info("clone_deleted", repo=repo_full_name)
            return True
        return False

    @staticmethod
    def get_clone_info(repo_full_name: str) -> dict | None:
        """Get info about an existing clone."""
        repo_path = CloneService.get_repo_path(repo_full_name)
        if not repo_path.exists():
            return None

        file_count = sum(1 for f in repo_path.rglob("*") if f.is_file() and ".git" not in str(f))
        total_size = sum(
            f.stat().st_size
            for f in repo_path.rglob("*")
            if f.is_file() and ".git" not in str(f)
        )

        return {
            "path": str(repo_path),
            "file_count": file_count,
            "total_size_bytes": total_size,
            "exists": True,
        }
