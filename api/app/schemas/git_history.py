"""
Synkora API — Git History Schemas

Pydantic models for representing Git commit history, contributor statistics,
code churn patterns, and file-level change frequency analysis.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CommitInfo(BaseModel):
    """Parsed metadata from a single Git commit."""
    sha: str
    short_sha: str
    message: str
    author_name: str
    author_email: str
    authored_at: datetime
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0
    net_lines: int = 0  # insertions - deletions


class ContributorStats(BaseModel):
    """Aggregated statistics for a single contributor."""
    name: str
    email: str
    commit_count: int = 0
    first_commit_at: Optional[datetime] = None
    last_commit_at: Optional[datetime] = None
    total_insertions: int = 0
    total_deletions: int = 0
    files_touched: int = 0
    avg_commit_size: float = 0.0  # Avg lines changed per commit

    @property
    def tenure_days(self) -> int:
        """Days between first and last commit."""
        if self.first_commit_at and self.last_commit_at:
            return max((self.last_commit_at - self.first_commit_at).days, 1)
        return 0

    @property
    def commits_per_day(self) -> float:
        """Average commits per day over active tenure."""
        if self.tenure_days > 0:
            return round(self.commit_count / self.tenure_days, 2)
        return 0.0


class FileChurn(BaseModel):
    """Change frequency metrics for a single file."""
    filepath: str
    change_count: int = 0       # Number of commits that touched this file
    total_insertions: int = 0
    total_deletions: int = 0
    distinct_authors: int = 0
    last_modified_at: Optional[datetime] = None

    @property
    def churn_score(self) -> float:
        """Higher = more frequently changed (potential hotspot)."""
        return self.change_count * (1 + self.distinct_authors * 0.2)

    @property
    def risk_level(self) -> str:
        if self.churn_score <= 5:
            return "low"
        elif self.churn_score <= 15:
            return "moderate"
        return "high"


class CommitFrequency(BaseModel):
    """Commit activity grouped by time period."""
    period: str        # e.g. "2024-01", "Monday", "14:00"
    commit_count: int = 0
    insertions: int = 0
    deletions: int = 0


class GitHistoryReport(BaseModel):
    """Complete Git history analysis for a repository."""
    total_commits: int = 0
    total_contributors: int = 0
    total_insertions: int = 0
    total_deletions: int = 0
    first_commit_at: Optional[datetime] = None
    last_commit_at: Optional[datetime] = None
    avg_commit_size: float = 0.0
    commits: list[CommitInfo] = []
    contributors: list[ContributorStats] = []
    file_churn: list[FileChurn] = []
    monthly_activity: list[CommitFrequency] = []
    daily_activity: list[CommitFrequency] = []   # By day of week

    @property
    def project_age_days(self) -> int:
        if self.first_commit_at and self.last_commit_at:
            return max((self.last_commit_at - self.first_commit_at).days, 1)
        return 0

    @property
    def bus_factor(self) -> int:
        """
        Minimum number of contributors who authored 50%+ of commits.
        A bus factor of 1 means the project is at risk if one person leaves.
        """
        if not self.contributors:
            return 0
        sorted_contributors = sorted(
            self.contributors, key=lambda c: c.commit_count, reverse=True
        )
        threshold = self.total_commits * 0.5
        running = 0
        for i, c in enumerate(sorted_contributors, 1):
            running += c.commit_count
            if running >= threshold:
                return i
        return len(sorted_contributors)
