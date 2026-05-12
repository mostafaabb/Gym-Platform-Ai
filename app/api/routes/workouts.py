from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.api.deps import get_db, get_current_user
from db.models import Workout, WorkoutLog, Exercise, User, WorkoutStatus, ExerciseSession

router = APIRouter(prefix="/workouts", tags=["workouts"])


class ExerciseLog(BaseModel):
    exercise_id: int
    set_number: int
    reps: int
    weight_kg: float | None = None
    notes: str | None = None


class WorkoutCreate(BaseModel):
    name: str
    goal: str
    exercises: list[int]


class WorkoutStart(BaseModel):
    name: str
    goal: str
    ai_plan: dict


class WorkoutResponse(BaseModel):
    id: int
    name: str
    goal: str
    status: WorkoutStatus
    started_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True


class WorkoutLogResponse(BaseModel):
    id: int
    exercise_id: int | None
    set_number: int
    reps: int
    weight_kg: float | None
    fatigue_score: int | None
    logged_at: datetime

    class Config:
        from_attributes = True


@router.post("/start", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
async def start_workout(
    request: WorkoutStart,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start new workout"""
    workout = Workout(
        user_id=current_user.id,
        name=request.name,
        goal=request.goal,
        status=WorkoutStatus.in_progress,
        ai_plan=request.ai_plan,
    )
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return WorkoutResponse.from_orm(workout)


@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get workout details"""
    workout = db.query(Workout).filter(Workout.id == workout_id).first()

    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")

    if workout.user_id != current_user.id and current_user.role.value != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't access this workout")

    return WorkoutResponse.from_orm(workout)


@router.post("/{workout_id}/log", response_model=WorkoutLogResponse, status_code=status.HTTP_201_CREATED)
async def log_workout(
    workout_id: int,
    request: ExerciseLog,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Log exercise during workout"""
    workout = db.query(Workout).filter(Workout.id == workout_id).first()

    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")

    if workout.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't log to this workout")

    exercise = db.query(Exercise).filter(Exercise.id == request.exercise_id).first() if request.exercise_id else None

    log = WorkoutLog(
        workout_id=workout_id,
        exercise_id=request.exercise_id,
        set_number=request.set_number,
        reps=request.reps,
        weight_kg=request.weight_kg,
        notes=request.notes,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return WorkoutLogResponse.from_orm(log)


@router.post("/{workout_id}/complete", response_model=WorkoutResponse)
async def complete_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark workout as completed"""
    workout = db.query(Workout).filter(Workout.id == workout_id).first()

    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")

    if workout.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't complete this workout")

    workout.status = WorkoutStatus.completed
    workout.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(workout)

    return WorkoutResponse.from_orm(workout)


@router.get("/user/{user_id}/history", response_model=list[WorkoutResponse])
async def get_workout_history(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user workout history"""
    if current_user.id != user_id and current_user.role.value != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't access this user's history")

    workouts = db.query(Workout).filter(Workout.user_id == user_id).offset(skip).limit(limit).all()
    return [WorkoutResponse.from_orm(w) for w in workouts]


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete workout"""
    workout = db.query(Workout).filter(Workout.id == workout_id).first()

    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")

    if workout.user_id != current_user.id and current_user.role.value != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't delete this workout")

    db.delete(workout)
    db.commit()
