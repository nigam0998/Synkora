"""
Synkora API — Git History Service

Mines Git commit history from cloned repositories using GitPython.
Extracts contributor statistics, code churn patterns, file change
frequency, and temporal activity analysis.
"""

import asyncio
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.schemas.git_history import (
    CommitInfo,
    ContributorStats,
    FileChurn,
    CommitFrequency,
    GitHistoryReport,
)
from app.core.logging import get_logger

logger = get_logger("git_history_service")


class GitHistoryService:
    """Service for mining and analyzing Git commit history."""

    @staticmethod
    async def analyze_repository(
        repo_path: Path,
        max_commits: int = 500,
        branch: Optional[str] = None,
    ) -> GitHistoryReport:
        """
        Perform a full Git history analysis on a local repository clone.

        Args:
            repo_path: Path to the cloned repository.
            max_commits: Maximum number of commits to analyze (most recent first).
            branch: Branch to analyze (defaults to active branch).

        Returns:
            Complete GitHistoryReport with commits, contributors, churn, and activity.
        """
        return await asyncio.to_thread(
            GitHistoryService._analyze_sync, repo_path, max_commits, branch
        )

    @staticmethod
    def _analyze_sync(
        repo_path: Path,
        max_commits: int,
        branch: Optional[str],
    ) -> GitHistoryReport:
        """Synchronous implementation — runs in a thread pool."""
        from git import Repo, InvalidGitRepositoryError

        try:
            repo = Repo(str(repo_path))
        except InvalidGitRepositoryError:
            logger.error("invalid_git_repo", path=str(repo_path))
            return GitHistoryReport()

        # ── 1. Parse commits ─────────────────────────────────────────────
        commits: list[CommitInfo] = []
        contributor_map: dict[str, ContributorStats] = {}
        file_change_map: dict[str, FileChurn] = defaultdict(
            lambda: FileChurn(filepath="")
        )
        monthly_map: dict[str, CommitFrequency] = {}
        daily_map: dict[str, CommitFrequency] = {}
        total_insertions = 0
        total_deletions = 0

        try:
            commit_iter = repo.iter_commits(branch or repo.active_branch, max_count=max_commits)
        except Exception as e:
            logger.warning("branch_error", error=str(e))
            try:
                commit_iter = repo.iter_commits(max_count=max_commits)
            except Exception:
                return GitHistoryReport()

        for commit in commit_iter:
            authored_at = datetime.fromtimestamp(
                commit.authored_date, tz=timezone.utc
            )

            # Diff stats
            stats = commit.stats.total
            insertions = stats.get("insertions", 0)
            deletions = stats.get("deletions", 0)
            files_changed = stats.get("files", 0)

            total_insertions += insertions
            total_deletions += deletions

            commit_info = CommitInfo(
                sha=commit.hexsha,
                short_sha=commit.hexsha[:7],
                message=commit.message.strip().split("\n")[0],  # First line only
                author_name=commit.author.name or "Unknown",
                author_email=commit.author.email or "unknown@unknown",
                authored_at=authored_at,
                files_changed=files_changed,
                insertions=insertions,
                deletions=deletions,
                net_lines=insertions - deletions,
            )
            commits.append(commit_info)

            # ── 2. Aggregate contributor stats ───────────────────────────
            email = commit_info.author_email.lower()
            if email not in contributor_map:
                contributor_map[email] = ContributorStats(
                    name=commit_info.author_name,
                    email=email,
                    first_commit_at=authored_at,
                    last_commit_at=authored_at,
                )

            contributor = contributor_map[email]
            contributor.commit_count += 1
            contributor.total_insertions += insertions
            contributor.total_deletions += deletions

            # Update time range (commits come newest-first)
            if contributor.first_commit_at is None or authored_at < contributor.first_commit_at:
                contributor.first_commit_at = authored_at
            if contributor.last_commit_at is None or authored_at > contributor.last_commit_at:
                contributor.last_commit_at = authored_at

            # ── 3. Aggregate file churn ──────────────────────────────────
            for filepath, file_stats in commit.stats.files.items():
                churn = file_change_map[filepath]
                if churn.filepath == "":
                    churn.filepath = filepath
                churn.change_count += 1
                churn.total_insertions += file_stats.get("insertions", 0)
                churn.total_deletions += file_stats.get("deletions", 0)
                if churn.last_modified_at is None or authored_at > churn.last_modified_at:
                    churn.last_modified_at = authored_at

            # ── 4. Aggregate temporal activity ───────────────────────────
            month_key = authored_at.strftime("%Y-%m")
            if month_key not in monthly_map:
                monthly_map[month_key] = CommitFrequency(period=month_key)
            monthly_map[month_key].commit_count += 1
            monthly_map[month_key].insertions += insertions
            monthly_map[month_key].deletions += deletions

            day_key = authored_at.strftime("%A")  # "Monday", "Tuesday", etc.
            if day_key not in daily_map:
                daily_map[day_key] = CommitFrequency(period=day_key)
            daily_map[day_key].commit_count += 1
            daily_map[day_key].insertions += insertions
            daily_map[day_key].deletions += deletions

        # ── 5. Post-processing ───────────────────────────────────────────

        # Calculate distinct authors per file
        # Re-iterate commits for author-per-file mapping
        file_authors: dict[str, set[str]] = defaultdict(set)
        for c in commits:
            # We need to get file list from the commit again
            # Use a simpler approach: for each file in file_change_map,
            # count contributors based on the commits we already parsed
            pass

        # Simpler approach: iterate commit stats for author tracking
        try:
            for commit in repo.iter_commits(branch or repo.active_branch, max_count=max_commits):
                author_email = (commit.author.email or "unknown").lower()
                for filepath in commit.stats.files:
                    file_authors[filepath].add(author_email)
        except Exception:
            pass

        for filepath, authors in file_authors.items():
            if filepath in file_change_map:
                file_change_map[filepath].distinct_authors = len(authors)

        # Calculate avg commit size per contributor
        for contributor in contributor_map.values():
            total_lines = contributor.total_insertions + contributor.total_deletions
            contributor.avg_commit_size = round(
                total_lines / max(contributor.commit_count, 1), 1
            )

        # Count files touched per contributor
        contributor_files: dict[str, set[str]] = defaultdict(set)
        for filepath, authors in file_authors.items():
            for author in authors:
                contributor_files[author].add(filepath)
        for email, files in contributor_files.items():
            if email in contributor_map:
                contributor_map[email].files_touched = len(files)

        # Sort results
        sorted_contributors = sorted(
            contributor_map.values(),
            key=lambda c: c.commit_count,
            reverse=True,
        )
        sorted_churn = sorted(
            [c for c in file_change_map.values() if c.filepath],
            key=lambda c: c.churn_score,
            reverse=True,
        )
        sorted_monthly = sorted(monthly_map.values(), key=lambda m: m.period)

        # Day-of-week ordering
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        sorted_daily = sorted(
            daily_map.values(),
            key=lambda d: day_order.index(d.period) if d.period in day_order else 7,
        )

        # Aggregate
        total_commits = len(commits)
        avg_size = (
            round((total_insertions + total_deletions) / max(total_commits, 1), 1)
        )
        first_commit = commits[-1].authored_at if commits else None
        last_commit = commits[0].authored_at if commits else None

        report = GitHistoryReport(
            total_commits=total_commits,
            total_contributors=len(sorted_contributors),
            total_insertions=total_insertions,
            total_deletions=total_deletions,
            first_commit_at=first_commit,
            last_commit_at=last_commit,
            avg_commit_size=avg_size,
            commits=commits,
            contributors=sorted_contributors,
            file_churn=sorted_churn[:50],  # Top 50 most churned files
            monthly_activity=sorted_monthly,
            daily_activity=sorted_daily,
        )

        logger.info(
            "git_history_analyzed",
            path=str(repo_path),
            commits=total_commits,
            contributors=len(sorted_contributors),
            files_churned=len(sorted_churn),
        )

        return report
