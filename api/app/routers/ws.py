"""
Synkora API — WebSocket Router

Provides a WebSocket endpoint for real-time analysis pipeline updates.
Clients connect to `/api/v1/ws/{repository_id}` and receive JSON messages
as the analysis pipeline progresses.

Message format:
    {
        "event": "pipeline_progress" | "pipeline_completed" | "pipeline_failed",
        "data": { ... }
    }
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.logging import get_logger
from app.services.ws_manager import ws_manager

logger = get_logger("ws_router")

router = APIRouter()


@router.websocket("/ws/{repository_id}")
async def pipeline_ws(websocket: WebSocket, repository_id: str):
    """
    WebSocket endpoint for streaming analysis progress.

    Clients connect here and receive real-time JSON events as the
    analysis pipeline processes a repository.
    """
    await ws_manager.connect(websocket, repository_id)

    try:
        # Keep connection alive — listen for client pings / close
        while True:
            data = await websocket.receive_text()
            # Clients can send "ping" to keep alive
            if data == "ping":
                await websocket.send_json({"event": "pong"})
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, repository_id)
    except Exception as e:
        logger.warning("ws_error", repo_id=repository_id, error=str(e))
        await ws_manager.disconnect(websocket, repository_id)
