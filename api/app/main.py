"""
Synkora API — Main Application Entry Point

Creates and configures the FastAPI application with all middleware,
routers, and lifecycle events.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.database import init_db, close_db
from app.routers import health, auth, repositories, analysis, github, webhooks


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager — startup and shutdown logic."""
    setup_logging()
    logger = get_logger("lifespan")
    logger.info(
        "starting_synkora_api",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )

    # Initialize database (create tables if needed)
    await init_db()

    yield

    # Cleanup database connections
    await close_db()
    logger.info("shutting_down_synkora_api")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ── CORS Middleware ──────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Register Routers ─────────────────────────────────────────────
    app.include_router(health.router, tags=["Health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(
        repositories.router, prefix="/api/v1/repositories", tags=["Repositories"]
    )
    app.include_router(
        analysis.router, prefix="/api/v1/analysis", tags=["Analysis"]
    )
    app.include_router(
        github.router, prefix="/api/v1/github", tags=["GitHub"]
    )
    app.include_router(
        webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"]
    )

    return app


# ── Application Instance ─────────────────────────────────────────────────
app = create_app()
