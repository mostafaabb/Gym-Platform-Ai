from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

from app.api.deps import get_db, get_current_user
from db.models import Class, ClassBooking, Trainer, User, ClassStatus, UserRole, Gym

router = APIRouter(prefix="/classes", tags=["classes"])


class ClassCreate(BaseModel):
    gym_id: int
    trainer_id: int
    name: str
    description: str | None = None
    class_type: str
    max_capacity: int = 20
    duration_minutes: int = 60
    start_time: datetime
    end_time: datetime
    price: Decimal = Decimal("0.00")
    location: str | None = None


class ClassResponse(BaseModel):
    id: int
    name: str
    description: str | None
    class_type: str
    max_capacity: int
    duration_minutes: int
    start_time: datetime
    end_time: datetime
    status: ClassStatus
    price: Decimal
    location: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class ClassBookingResponse(BaseModel):
    id: int
    class_id: int
    user_id: int
    booked_at: datetime
    status: str

    class Config:
        from_attributes = True


@router.post("", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
async def create_class(
    request: ClassCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create class"""
    if current_user.role not in [UserRole.super_admin, UserRole.trainer]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only trainers can create classes")

    trainer = db.query(Trainer).filter(Trainer.id == request.trainer_id, Trainer.user_id == current_user.id).first()
    if not trainer and current_user.role != UserRole.super_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only create classes for yourself")

    class_obj = Class(
        gym_id=request.gym_id,
        trainer_id=request.trainer_id,
        name=request.name,
        description=request.description,
        class_type=request.class_type,
        max_capacity=request.max_capacity,
        duration_minutes=request.duration_minutes,
        start_time=request.start_time,
        end_time=request.end_time,
        status=ClassStatus.scheduled,
        price=request.price,
        location=request.location,
    )
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    return ClassResponse.from_orm(class_obj)


@router.get("/{class_id}", response_model=ClassResponse)
async def get_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get class details"""
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")

    return ClassResponse.from_orm(class_obj)


@router.post("/{class_id}/book", response_model=ClassBookingResponse, status_code=status.HTTP_201_CREATED)
async def book_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Book class"""
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")

    existing_booking = db.query(ClassBooking).filter(
        ClassBooking.class_id == class_id,
        ClassBooking.user_id == current_user.id
    ).first()
    if existing_booking:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already booked this class")

    bookings_count = db.query(ClassBooking).filter(ClassBooking.class_id == class_id).count()
    if bookings_count >= class_obj.max_capacity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Class is full")

    booking = ClassBooking(
        class_id=class_id,
        user_id=current_user.id,
        status="booked"
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return ClassBookingResponse.from_orm(booking)


@router.post("/{class_id}/cancel-booking", status_code=status.HTTP_200_OK)
async def cancel_class_booking(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancel class booking"""
    booking = db.query(ClassBooking).filter(
        ClassBooking.class_id == class_id,
        ClassBooking.user_id == current_user.id
    ).first()

    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    booking.status = "canceled"
    db.commit()
    return {"message": "Booking canceled"}


@router.get("/gym/{gym_id}/list", response_model=list[ClassResponse])
async def get_gym_classes(
    gym_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get classes in gym"""
    classes = db.query(Class).filter(Class.gym_id == gym_id).offset(skip).limit(limit).all()
    return [ClassResponse.from_orm(c) for c in classes]
