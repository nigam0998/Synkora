"""
Synkora API — Webhook Schemas

Pydantic models for GitHub webhook events.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WebhookEventBase(BaseModel):
    """Base schema for all webhook events."""
    event_type: str
    delivery_id: Optional[str] = None
    received_at: datetime


class PushEventCommit(BaseModel):
    """A single commit within a push event."""
    sha: str
    message: str
    author_name: str
    author_email: str
    timestamp: str
    added: list[str] = []
    removed: list[str] = []
    modified: list[str] = []


class PushEvent(WebhookEventBase):
    """GitHub push event data."""
    ref: str  # e.g. "refs/heads/main"
    before: str  # SHA before push
    after: str  # SHA after push
    repository_id: int
    repository_full_name: str
    pusher_name: str
    commits: list[PushEventCommit] = []
    head_commit: Optional[PushEventCommit] = None

    @property
    def branch(self) -> str:
        """Extract branch name from ref."""
        return self.ref.replace("refs/heads/", "")


class WebhookResponse(BaseModel):
    """Response returned from webhook endpoints."""
    status: str  # accepted | ignored | error
    message: str
    task_id: Optional[str] = None
