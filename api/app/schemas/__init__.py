"""
Synkora API — Schema Package

Pydantic models for API request/response validation and serialization.
Organized by domain:
  - auth: Registration, login, token, and user response models
  - repository: Repository CRUD models
  - analysis: Analysis results and insight models
  - webhook: GitHub webhook event models
  - ast: Abstract Syntax Tree data models
  - metrics: Code quality metric models
  - dependency: Dependency graph models
  - tech_debt: Technical debt issues and reports
"""

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
    AuthResponse,
    MessageResponse,
)
from app.schemas.repository import (
    RepositoryCreate,
    RepositoryResponse,
    RepositoryListResponse,
)
from app.schemas.analysis import (
    AnalysisResponse,
    InsightResponse,
    AnalysisDetailResponse,
)
from app.schemas.webhook import WebhookResponse
from app.schemas.ast import ParsedFile, FunctionDef, ClassDef, ImportDef
from app.schemas.metrics import FunctionMetrics, ClassMetrics, FileMetrics, RepositoryMetrics
from app.schemas.dependency import DependencyNode, DependencyEdge, DependencyGraph
from app.schemas.tech_debt import TechDebtIssue, TechDebtReport

__all__ = [
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "RefreshTokenRequest",
    "TokenResponse",
    "UserResponse",
    "AuthResponse",
    "MessageResponse",
    # Repository
    "RepositoryCreate",
    "RepositoryResponse",
    "RepositoryListResponse",
    # Analysis
    "AnalysisResponse",
    "InsightResponse",
    "AnalysisDetailResponse",
    # Webhooks
    "WebhookResponse",
    # AST
    "ParsedFile",
    "FunctionDef",
    "ClassDef",
    "ImportDef",
    # Metrics
    "FunctionMetrics",
    "ClassMetrics",
    "FileMetrics",
    "RepositoryMetrics",
    # Dependencies
    "DependencyNode",
    "DependencyEdge",
    "DependencyGraph",
    # Tech Debt
    "TechDebtIssue",
    "TechDebtReport",
]
