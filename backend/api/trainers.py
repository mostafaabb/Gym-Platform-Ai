from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.core.exceptions import ResourceNotFoundException
from backend.models import Trainer, TrainingSession, Member
from backend.schemas import TrainerCreateRequest, TrainerResponse
from backend.repositories.repositories import TrainerRepository, MemberRepository
from datetime import datetime

router = APIRouter(prefix="/trainers", tags=["Trainers"])
trainer_repo = TrainerRepository()
member_repo = MemberRepository()


@router.post("", response_model=TrainerResponse, status_code=status.HTTP_201_CREATED)
async def create_trainer(request: TrainerCreateRequest, db: AsyncSession = Depends(get_db)):
    """Create a new trainer."""
    trainer = Trainer(
        user_id=request.user_id,
        gym_id=request.gym_id,
        bio=request.bio,
        specialties=request.specialties,
        certifications=request.certifications,
        hourly_rate=request.hourly_rate,
    )
    db.add(trainer)
    await db.commit()
    await db.refresh(trainer)

    return TrainerResponse.model_validate(trainer)


@router.get("/{trainer_id}", response_model=TrainerResponse)
async def get_trainer(trainer_id: int, db: AsyncSession = Depends(get_db)):
    """Get trainer details."""
    trainer = await trainer_repo.get(db, trainer_id)
    if not trainer:
        raise ResourceNotFoundException("Trainer not found")

    return TrainerResponse.model_validate(trainer)


@router.get("/gym/{gym_id}", response_model=list[TrainerResponse])
async def get_gym_trainers(gym_id: int, db: AsyncSession = Depends(get_db)):
    """Get all trainers in a gym."""
    trainers = await trainer_repo.get_gym_trainers(db, gym_id)
    return [TrainerResponse.model_validate(t) for t in trainers]


@router.post("/{trainer_id}/schedule-session")
async def schedule_training_session(
    trainer_id: int,
    member_id: int,
    start_time: datetime,
    duration_minutes: int = 60,
    db: AsyncSession = Depends(get_db)
):
    """Schedule a training session with a trainer."""
    trainer = await trainer_repo.get(db, trainer_id)
    if not trainer:
        raise ResourceNotFoundException("Trainer not found")

    member = await member_repo.get(db, member_id)
    if not member:
        raise ResourceNotFoundException("Member not found")

    session = TrainingSession(
        trainer_id=trainer_id,
        member_id=member_id,
        start_time=start_time,
        status="scheduled"
    )
    db.add(session)
    await db.commit()

    return {
        "session_id": session.id,
        "trainer_id": trainer_id,
        "member_id": member_id,
        "start_time": start_time,
        "status": "scheduled"
    }


@router.get("/{trainer_id}/clients")
async def get_trainer_clients(trainer_id: int, db: AsyncSession = Depends(get_db)):
    """Get all clients of a trainer."""
    trainer = await trainer_repo.get(db, trainer_id)
    if not trainer:
        raise ResourceNotFoundException("Trainer not found")

    result = await db.execute(
        __import__('sqlalchemy').select(TrainingSession)
        .where(TrainingSession.trainer_id == trainer_id)
        .distinct()
    )
    sessions = result.scalars().all()

    client_ids = list(set(s.member_id for s in sessions))
    clients = [await member_repo.get(db, cid) for cid in client_ids]

    return {
        "trainer_id": trainer_id,
        "total_clients": len(clients),
        "clients": [{"id": c.id, "user_id": c.user_id} for c in clients if c]
    }

from backend.services.ai_service import ai_service

@router.get("/{trainer_id}/copilot-brief")
async def get_trainer_copilot_brief(trainer_id: int, db: AsyncSession = Depends(get_db)):
    """Trainer Copilot: Generates an AI morning brief for trainers."""
    # Mock data aggregation for clients
    clients_data = [
        {"name": "John Doe", "days_streak": 5, "acwr_risk": "High", "recent_logs": "Dropped nutrition"},
        {"name": "Sarah Smith", "days_streak": 2, "acwr_risk": "Low", "recent_logs": "Consistent"}
    ]
    brief = await ai_service.generate_trainer_brief(clients_data)
    return {"trainer_id": trainer_id, "brief": brief}
