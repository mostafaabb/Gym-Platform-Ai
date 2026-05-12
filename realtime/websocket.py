import json
from datetime import datetime
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from sqlalchemy.orm import Session
import logging

from app.api.deps import get_db
from app.core.auth import verify_token
from db.models import User, Conversation

router = APIRouter(prefix="", tags=["websocket"])
logger = logging.getLogger(__name__)

# Store active connections
active_connections: Dict[int, Set[WebSocket]] = {}


class ConnectionManager:
    """Manage WebSocket connections"""

    @staticmethod
    async def connect(user_id: int, websocket: WebSocket):
        """Register new connection"""
        await websocket.accept()
        if user_id not in active_connections:
            active_connections[user_id] = set()
        active_connections[user_id].add(websocket)
        logger.info(f"User {user_id} connected. Total connections: {len(active_connections[user_id])}")

    @staticmethod
    async def disconnect(user_id: int, websocket: WebSocket):
        """Unregister connection"""
        if user_id in active_connections:
            active_connections[user_id].discard(websocket)
            if not active_connections[user_id]:
                del active_connections[user_id]
        logger.info(f"User {user_id} disconnected")

    @staticmethod
    async def broadcast_to_user(user_id: int, message: dict):
        """Send message to all user connections"""
        if user_id in active_connections:
            disconnected = set()
            for connection in active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message: {e}")
                    disconnected.add(connection)

            for conn in disconnected:
                await ConnectionManager.disconnect(user_id, conn)

    @staticmethod
    async def broadcast_to_all(message: dict):
        """Broadcast to all connected users"""
        for user_id in list(active_connections.keys()):
            await ConnectionManager.broadcast_to_user(user_id, message)


@router.websocket("/ws/voice")
async def websocket_voice_coach(websocket: WebSocket, token: str = Query(...), db: Session = Depends(get_db)):
    """WebSocket endpoint for AI voice coaching"""
    # Verify token
    token_data = verify_token(token, token_type="access")
    if token_data is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return

    user_id = int(token_data.sub)
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
        return

    await ConnectionManager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Process user message
            user_message = message_data.get("message", "")

            if not user_message:
                await websocket.send_json({"error": "Empty message"})
                continue

            # Here you would call your AI coaching service
            # For now, send a simple response
            ai_response = f"Acknowledged: {user_message}"

            # Store conversation
            conversation = Conversation(
                user_id=user_id,
                source="voice",
                user_message=user_message,
                ai_message=ai_response,
                agent_name="voice_coach",
            )
            db.add(conversation)
            db.commit()

            # Send response
            await websocket.send_json({
                "type": "ai_response",
                "message": ai_response,
                "timestamp": datetime.utcnow().isoformat(),
            })

    except WebSocketDisconnect:
        await ConnectionManager.disconnect(user_id, websocket)
        logger.info(f"Voice connection disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await ConnectionManager.disconnect(user_id, websocket)


@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket, token: str = Query(...), db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time notifications"""
    token_data = verify_token(token, token_type="access")
    if token_data is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return

    user_id = int(token_data.sub)
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
        return

    await ConnectionManager.connect(user_id, websocket)

    try:
        while True:
            await websocket.receive_text()
            # Keep connection alive, server sends notifications via broadcast

    except WebSocketDisconnect:
        await ConnectionManager.disconnect(user_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket notification error: {e}")
        await ConnectionManager.disconnect(user_id, websocket)


@router.websocket("/ws/live-workout")
async def websocket_live_workout(websocket: WebSocket, token: str = Query(...), db: Session = Depends(get_db)):
    """WebSocket endpoint for live workout monitoring"""
    token_data = verify_token(token, token_type="access")
    if token_data is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return

    user_id = int(token_data.sub)
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
        return

    await ConnectionManager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            workout_data = json.loads(data)

            # Process live workout data (pose, form, metrics, etc)
            response = {
                "type": "workout_update",
                "data": workout_data,
                "timestamp": datetime.utcnow().isoformat(),
            }

            await websocket.send_json(response)

    except WebSocketDisconnect:
        await ConnectionManager.disconnect(user_id, websocket)
    except Exception as e:
        logger.error(f"Live workout error: {e}")
        await ConnectionManager.disconnect(user_id, websocket)
