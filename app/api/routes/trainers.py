from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

from app.api.deps import get_db, get_current_user
from db.models import Trainer, User, UserRole, Gym

router = APIRouter(prefix="/trainers", tags=["trainers"])


class TrainerCreate(BaseModel):
    gym_id: int
    specialization: str
    certification: str | None = None
    bio: str | None = None
    hourly_rate: Decimal = Decimal("50.00")
    experience_years: int = 0


class TrainerResponse(BaseModel):
    id: int
    user_id: int
    gym_id: int
    specialization: str
    certification: str | None
    bio: str | None
    hourly_rate: Decimal
    rating: float
    experience_years: int
    is_available: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TrainerUpdate(BaseModel):
    specialization: str | None = None
    certification: str | None = None
    bio: str | None = None
    hourly_rate: Decimal | None = None
    experience_years: int | None = None
    is_available: bool | None = None


@router.post("", response_model=TrainerResponse, status_code=status.HTTP_201_CREATED)
async def create_trainer(
    request: TrainerCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create trainer profile"""
    if current_user.role not in [UserRole.super_admin, UserRole.trainer]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only trainers can create trainer profiles")

    existing = db.query(Trainer).filter(Trainer.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Trainer profile already exists")

    gym = db.query(Gym).filter(Gym.id == request.gym_id).first()
    if not gym:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gym not found")

    trainer = Trainer(
        user_id=current_user.id,
        gym_id=request.gym_id,
        specialization=request.specialization,
        certification=request.certification,
        bio=request.bio,
        hourly_rate=request.hourly_rate,
        experience_years=request.experience_years,
    )
    db.add(trainer)
    db.commit()
    db.refresh(trainer)
    return TrainerResponse.from_orm(trainer)


@router.get("/{trainer_id}", response_model=TrainerResponse)
async def get_trainer(
    trainer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get trainer profile"""
    trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
    if not trainer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trainer not found")

    return TrainerResponse.from_orm(trainer)


@router.put("/{trainer_id}", response_model=TrainerResponse)
async def update_trainer(
    trainer_id: int,
    request: TrainerUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update trainer profile"""
    trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
    if not trainer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trainer not found")

    if trainer.user_id != current_user.id and current_user.role != UserRole.super_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't update this trainer")

    if request.specialization:
        trainer.specialization = request.specialization
    if request.certification:
        trainer.certification = request.certification
    if request.bio:
        trainer.bio = request.bio
    if request.hourly_rate:
        trainer.hourly_rate = request.hourly_rate
    if request.experience_years is not None:
        trainer.experience_years = request.experience_years
    if request.is_available is not None:
        trainer.is_available = request.is_available

    db.commit()
    db.refresh(trainer)
    return TrainerResponse.from_orm(trainer)


@router.get("/gym/{gym_id}/list", response_model=list[TrainerResponse])
async def get_gym_trainers(
    gym_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get trainers in gym"""
    trainers = db.query(Trainer).filter(Trainer.gym_id == gym_id).offset(skip).limit(limit).all()
    return [TrainerResponse.from_orm(t) for t in trainers]
