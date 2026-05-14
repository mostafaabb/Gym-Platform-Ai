from fastapi import APIRouter, Depends, status, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.core.exceptions import ResourceNotFoundException
from backend.models import AISession, User
from backend.schemas import AIMessageRequest, AISessionResponse
from backend.repositories.repositories import UserRepository
import json

router = APIRouter(prefix="/ai", tags=["AI"])
user_repo = UserRepository()


@router.post("/sessions", response_model=AISessionResponse, status_code=status.HTTP_201_CREATED)
async def create_ai_session(
    session_type: str = "voice_coach",
    db: AsyncSession = Depends(get_db)
):
    """Create a new AI session."""
    ai_session = AISession(
        user_id=1,  # TODO: Get from auth context
        session_type=session_type,
    )
    db.add(ai_session)
    await db.commit()
    await db.refresh(ai_session)

    return AISessionResponse.model_validate(ai_session)


@router.post("/sessions/{session_id}/messages")
async def send_ai_message(
    session_id: int,
    request: AIMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send message to AI coach and get response."""
    from backend.services.ai_service import ai_service
    
    session = await db.get(AISession, session_id)
    if not session:
        raise ResourceNotFoundException("AI session not found")

    ai_response = await ai_service.get_voice_coach_response(
        request.message, 
        [], # History would be fetched from DB normally
        {"first_name": "Member"}
    )

    return {
        "id": session_id,
        "user_message": request.message,
        "ai_response": ai_response,
        "timestamp": str(__import__('datetime').datetime.utcnow()),
    }


@router.post("/generate-workout/{member_id}")
async def generate_personalized_workout(
    member_id: int,
    goal: str = "muscle_gain",
    db: AsyncSession = Depends(get_db)
):
    """Generate a personalized workout using AI."""
    from backend.services.workout_service import workout_service
    workout = await workout_service.create_personalized_workout(db, member_id, goal)
    return workout


@router.post("/nutrition-plan/{member_id}")
async def generate_nutrition_plan(
    member_id: int,
    goal: str = "muscle_gain",
    db: AsyncSession = Depends(get_db)
):
    """Generate personalized nutrition plan using AI."""
    from backend.services.nutrition_service import nutrition_service
    plan = await nutrition_service.generate_meal_plan(db, member_id, goal)
    return plan


@router.post("/posture-analysis/{workout_id}")
async def analyze_workout_posture(
    workout_id: int,
    frame_data: list[dict] = None,
    db: AsyncSession = Depends(get_db)
):
    """Analyze posture during workout using pose detection."""
    from backend.services.ai_service import ai_service
    analysis = await ai_service.analyze_pose_landmarks(frame_data or [], "squat")
    return analysis


@router.get("/injury-prediction/{member_id}")
async def predict_injury_risk(member_id: int, db: AsyncSession = Depends(get_db)):
    """Predict injury risk based on member data and history."""
    # TODO: Implement injury prediction model
    return {
        "member_id": member_id,
        "injury_risk_score": 15.3,
        "risk_level": "low",
        "risk_factors": [],
        "recommendations": [
            "Increase warm-up duration",
            "Focus on mobility work"
        ]
    }


@router.post("/voice-chat/{member_id}")
async def create_voice_chat_session(member_id: int, db: AsyncSession = Depends(get_db)):
    """Create a voice chat session with AI coach."""
    # TODO: Implement voice coaching with Whisper + TTS
    return {
        "member_id": member_id,
        "session_id": "voice_session_123",
        "websocket_url": "ws://localhost:8000/ws/voice/voice_session_123",
        "status": "ready"
    }
