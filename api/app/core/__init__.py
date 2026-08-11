"""
Synkora API — Core Package

Infrastructure layer providing cross-cutting concerns:
  - config: Centralized settings via Pydantic BaseSettings
  - database: Async SQLAlchemy engine and session management
  - dependencies: FastAPI dependency injection (auth, DB sessions)
  - logging: Structured logging with structlog
  - security: JWT token creation, verification, and password hashing
  - task_manager: Background task execution and progress tracking
  - webhook_verify: GitHub webhook signature validation
"""
