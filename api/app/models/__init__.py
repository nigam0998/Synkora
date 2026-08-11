"""
Synkora API — Model Package

SQLAlchemy ORM models representing the database schema:
  - User: User accounts with GitHub OAuth integration
  - Repository: Connected GitHub repositories
  - Analysis: Code analysis snapshots (metrics, language breakdown)
  - CommitRecord: Individual commit metadata for history mining
  - Insight: AI-generated code quality insights
"""

from app.models.base import Base
from app.models.user import User
from app.models.repository import Repository
from app.models.analysis import Analysis
from app.models.commit import CommitRecord
from app.models.insight import Insight

__all__ = [
    "Base",
    "User",
    "Repository",
    "Analysis",
    "CommitRecord",
    "Insight",
]
