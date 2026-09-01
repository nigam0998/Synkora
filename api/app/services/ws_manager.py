"""
Synkora API — WebSocket Manager

Manages WebSocket connections for real-time analysis pipeline updates.
Clients can subscribe to repository events and receive live progress
notifications as analyses run.
"""

import asyncio
from typing import Dict, Set
from fastapi import WebSocket

from app.core.logging import get_logger

logger = get_logger("ws_manager")


class ConnectionManager:
    """
    Manages active WebSocket connections, grouped by repository ID.

    Supports broadcasting pipeline events to all clients watching
    a specific repository.
    """

    def __init__(self):
        # repo_id -> set of active WebSocket connections
        self._connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, repository_id: str) -> None:
        """Accept a new WebSocket and register it for a repository."""
        await websocket.accept()
        async with self._lock:
            if repository_id not in self._connections:
                self._connections[repository_id] = set()
            self._connections[repository_id].add(websocket)
        logger.info(
            "ws_connected",
            repo_id=repository_id,
            total=len(self._connections.get(repository_id, set())),
        )

    async def disconnect(self, websocket: WebSocket, repository_id: str) -> None:
        """Remove a WebSocket from the registry."""
        async with self._lock:
            if repository_id in self._connections:
                self._connections[repository_id].discard(websocket)
                if not self._connections[repository_id]:
                    del self._connections[repository_id]
        logger.info("ws_disconnected", repo_id=repository_id)

    async def broadcast(self, repository_id: str, message: dict) -> None:
        """Send a JSON message to all clients watching a repository."""
        async with self._lock:
            connections = self._connections.get(repository_id, set()).copy()

        if not connections:
            return

        stale: list[WebSocket] = []
        for ws in connections:
            try:
                await ws.send_json(message)
            except Exception:
                stale.append(ws)

        # Clean up broken connections
        if stale:
            async with self._lock:
                for ws in stale:
                    self._connections.get(repository_id, set()).discard(ws)

    def active_count(self, repository_id: str | None = None) -> int:
        """Return the number of active connections (optionally filtered by repo)."""
        if repository_id:
            return len(self._connections.get(repository_id, set()))
        return sum(len(v) for v in self._connections.values())


# Singleton instance used across the application
ws_manager = ConnectionManager()
