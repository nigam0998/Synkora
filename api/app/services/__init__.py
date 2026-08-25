"""
Synkora API — Service Package

Business logic layer implementing the core platform capabilities:
  - auth_service: User authentication (register, login, token refresh)
  - github_service: GitHub API integration (OAuth, repos, profiles)
  - clone_service: Repository cloning and local storage management
  - repo_service: Connected repository CRUD operations
  - ast_service: Multi-language AST parsing via Tree-sitter
  - metrics_service: Code quality metrics (complexity, maintainability)
  - dependency_service: Dependency graph construction and analysis
  - git_history_service: Git commit mining, contributor stats, code churn
  - tech_debt_service: Tech debt detection and rule engine
"""

from app.services.auth_service import AuthService
from app.services.github_service import GitHubService
from app.services.clone_service import CloneService
from app.services.repo_service import RepositoryService
from app.services.ast_service import ASTService
from app.services.metrics_service import MetricsService
from app.services.dependency_service import DependencyService
from app.services.git_history_service import GitHistoryService
from app.services.tech_debt_service import TechDebtService
from app.services.analysis_orchestrator import AnalysisOrchestrator

__all__ = [
    "AuthService",
    "GitHubService",
    "CloneService",
    "RepositoryService",
    "ASTService",
    "MetricsService",
    "DependencyService",
    "GitHistoryService",
    "TechDebtService",
    "AnalysisOrchestrator",
]
