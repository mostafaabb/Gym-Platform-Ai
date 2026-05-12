from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.core.rbac import PermissionChecker
from db.models import Gym, User, Membership, MembershipStatus, UserRole

router = APIRouter(prefix="/gyms", tags=["gyms"])


class GymCreate(BaseModel):
    name: str
    location: str
    phone: str | None = None
    website: str | None = None
    capacity: int = 100
    operating_hours: dict | None = None
    amenities: dict | None = None


class GymResponse(BaseModel):
    id: int
    name: str
    location: str
    owner_email: str
    phone: str | None
    website: str | None
    total_members: int
    total_trainers: int
    capacity: int
    amenities: dict
    operating_hours: dict
    created_at: datetime

    class Config:
        from_attributes = True


class GymStats(BaseModel):
    total_members: int
    total_trainers: int
    active_classes: int
    revenue_month: float
    peak_hours: list


@router.post("", response_model=GymResponse, status_code=status.HTTP_201_CREATED)
async def create_gym(
    request: GymCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create gym (gym owner only)"""
    if current_user.role not in [UserRole.super_admin, UserRole.gym_owner]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only gym owners can create gyms")

    gym = Gym(
        name=request.name,
        location=request.location,
        owner_email=current_user.email,
        phone=request.phone,
        website=request.website,
        capacity=request.capacity,
        operating_hours=request.operating_hours or {},
        amenities=request.amenities or {},
    )
    db.add(gym)
    db.commit()
    db.refresh(gym)
    return GymResponse.from_orm(gym)


@router.get("/{gym_id}", response_model=GymResponse)
async def get_gym(
    gym_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get gym details"""
    gym = db.query(Gym).filter(Gym.id == gym_id).first()
    if not gym:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gym not found")

    return GymResponse.from_orm(gym)


@router.put("/{gym_id}", response_model=GymResponse)
async def update_gym(
    gym_id: int,
    request: GymCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update gym (owner only)"""
    gym = db.query(Gym).filter(Gym.id == gym_id).first()
    if not gym:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gym not found")

    if not PermissionChecker.can_manage_gym(current_user, gym_id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't update this gym")

    gym.name = request.name
    gym.location = request.location
    if request.phone:
        gym.phone = request.phone
    if request.website:
        gym.website = request.website
    gym.capacity = request.capacity
    if request.operating_hours:
        gym.operating_hours = request.operating_hours
    if request.amenities:
        gym.amenities = request.amenities

    db.commit()
    db.refresh(gym)
    return GymResponse.from_orm(gym)


@router.get("/{gym_id}/stats", response_model=GymStats)
async def get_gym_stats(
    gym_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get gym statistics"""
    gym = db.query(Gym).filter(Gym.id == gym_id).first()
    if not gym:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gym not found")

    members = db.query(Membership).filter(Membership.gym_id == gym_id, Membership.status == MembershipStatus.active).count()
    trainers = db.query(User).filter(User.role == UserRole.trainer).count()

    return GymStats(
        total_members=members,
        total_trainers=trainers,
        active_classes=0,
        revenue_month=0.0,
        peak_hours=[]
    )


@router.get("", response_model=list[GymResponse])
async def list_gyms(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all gyms"""
    gyms = db.query(Gym).offset(skip).limit(limit).all()
    return [GymResponse.from_orm(g) for g in gyms]
