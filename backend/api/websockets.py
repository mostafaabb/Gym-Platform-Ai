import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Set, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.rbac import decode_token
from backend.models import User, AISession, PoseAnalysisEvent
from backend.repositories.repositories import UserRepository
from backend.services.ai_service import ai_service

router = APIRouter(prefix="/ws", tags=["WebSockets"])
logger = logging.getLogger(__name__)
user_repo = UserRepository()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/coach")
async def coach_websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Unified WebSocket for AI Voice Coaching and Pose Analysis.
    Handles:
    - Text/Voice messages (via STT result from client)
    - Pose landmarks (MediaPipe)
    - Real-time feedback
    """
    # 1. Auth
    try:
        payload = decode_token(token)
        user_id = int(payload["sub"])
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user = await user_repo.get(db, user_id)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(user_id, websocket)
    
    # Track conversation history for this session
    session_history = []
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type")

            if msg_type == "user_message":
                # Handle text/voice input
                content = message.get("content")
                ai_response = await ai_service.get_voice_coach_response(
                    content, 
                    session_history,
                    {"first_name": user.first_name, "fitness_goal": "Strength"} # Mock context
                )
                
                session_history.append({"role": "user", "content": content})
                session_history.append({"role": "ai", "content": ai_response})
                
                await websocket.send_json({
                    "type": "ai_response",
                    "content": ai_response,
                    "timestamp": datetime.utcnow().isoformat()
                })

            elif msg_type == "pose_landmarks":
                # Handle real-time pose analysis
                landmarks = message.get("landmarks")
                exercise = message.get("exercise", "squat")
                
                analysis = await ai_service.analyze_pose_landmarks(landmarks, exercise)
                
                if analysis["alerts"]:
                    await websocket.send_json({
                        "type": "form_alert",
                        "content": analysis["alerts"][0],
                        "score": analysis["score"]
                    })
                
                # Periodically save analysis events to DB (using a background task ideally)
                # For simplicity, we just log it here
                logger.debug(f"Pose Analysis for {user.email}: {analysis['score']}")

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
        manager.disconnect(user_id, websocket)
