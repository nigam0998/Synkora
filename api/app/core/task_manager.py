"""
Synkora API — Background Task Manager

Simple in-process async task runner for background operations
like repository cloning, analysis, etc.

Note: In production, this should be replaced with a proper task queue
(e.g., Celery + Redis, or ARQ). This serves as the interface layer.
"""

import asyncio
from typing import Any, Callable, Coroutine
from datetime import datetime, timezone

from app.core.logging import get_logger

logger = get_logger("task_manager")


class TaskStatus:
    """Represents the status of a background task."""

    def __init__(self, task_id: str, name: str):
        self.task_id = task_id
        self.name = name
        self.status: str = "queued"  # queued | running | completed | failed
        self.progress: float = 0.0
        self.message: str = ""
        self.result: Any = None
        self.error: str | None = None
        self.created_at: datetime = datetime.now(timezone.utc)
        self.started_at: datetime | None = None
        self.completed_at: datetime | None = None

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


# ── In-memory task registry ─────────────────────────────────────────────
_tasks: dict[str, TaskStatus] = {}
_task_counter = 0


def _next_task_id() -> str:
    global _task_counter
    _task_counter += 1
    return f"task-{_task_counter:06d}"


async def submit_task(
    name: str,
    coro_fn: Callable[..., Coroutine],
    *args: Any,
    **kwargs: Any,
) -> TaskStatus:
    """
    Submit a coroutine to run as a background task.

    Args:
        name: Human-readable name for the task.
        coro_fn: An async function to execute.
        *args, **kwargs: Arguments passed to coro_fn.

    Returns:
        TaskStatus object for tracking progress.
    """
    task_id = _next_task_id()
    task_status = TaskStatus(task_id, name)
    _tasks[task_id] = task_status

    async def _run():
        task_status.status = "running"
        task_status.started_at = datetime.now(timezone.utc)
        logger.info("task_started", task_id=task_id, name=name)

        try:
            result = await coro_fn(task_status, *args, **kwargs)
            task_status.status = "completed"
            task_status.result = result
            task_status.progress = 100.0
            task_status.completed_at = datetime.now(timezone.utc)
            logger.info("task_completed", task_id=task_id, name=name)
        except Exception as e:
            task_status.status = "failed"
            task_status.error = str(e)
            task_status.completed_at = datetime.now(timezone.utc)
            logger.error("task_failed", task_id=task_id, name=name, error=str(e))

    asyncio.create_task(_run())
    return task_status


def get_task(task_id: str) -> TaskStatus | None:
    """Get the status of a task by ID."""
    return _tasks.get(task_id)


def list_tasks(limit: int = 20) -> list[dict]:
    """List recent tasks, newest first."""
    sorted_tasks = sorted(
        _tasks.values(),
        key=lambda t: t.created_at,
        reverse=True,
    )
    return [t.to_dict() for t in sorted_tasks[:limit]]
