from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from backend.core.database import get_db
from backend.core.exceptions import ResourceNotFoundException, ValidationException
from backend.models import Workout, WorkoutExercise, Member
from backend.schemas import WorkoutCreateRequest, WorkoutResponse
from backend.repositories.repositories import WorkoutRepository, MemberRepository

router = APIRouter(prefix="/members/{member_id}/workouts", tags=["Workouts"])
workout_repo = WorkoutRepository()
member_repo = MemberRepository()


@router.post("", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
async def create_workout(
    member_id: int,
    request: WorkoutCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new workout for a member."""
    member = await member_repo.get(db, member_id)
    if not member:
        raise ResourceNotFoundException("Member not found")

    workout = Workout(
        member_id=member_id,
        workout_type=request.workout_type,
        name=request.name or f"{request.workout_type} Workout",
        description=request.description,
        duration_minutes=request.duration_minutes,
        start_time=datetime.utcnow(),
    )
    db.add(workout)
    await db.commit()
    await db.refresh(workout)

    return WorkoutResponse.model_validate(workout)


@router.get("", response_model=list[WorkoutResponse])
async def get_member_workouts(
    member_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get workouts for a member."""
    member = await member_repo.get(db, member_id)
    if not member:
        raise ResourceNotFoundException("Member not found")

    workouts = await workout_repo.get_member_workouts(db, member_id, limit=limit + skip)
    return [WorkoutResponse.model_validate(w) for w in workouts[skip:skip+limit]]


@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(
    member_id: int,
    workout_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific workout."""
    workout = await workout_repo.get(db, workout_id)
    if not workout or workout.member_id != member_id:
        raise ResourceNotFoundException("Workout not found")

    return WorkoutResponse.model_validate(workout)


@router.put("/{workout_id}", response_model=WorkoutResponse)
async def update_workout(
    member_id: int,
    workout_id: int,
    request: WorkoutCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update a workout."""
    workout = await workout_repo.get(db, workout_id)
    if not workout or workout.member_id != member_id:
        raise ResourceNotFoundException("Workout not found")

    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key != "exercises":
            setattr(workout, key, value)

    db.add(workout)
    await db.commit()
    await db.refresh(workout)

    return WorkoutResponse.model_validate(workout)


@router.post("/{workout_id}/complete", response_model=WorkoutResponse)
async def complete_workout(
    member_id: int,
    workout_id: int,
    calories_burned: float = Query(None, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Mark workout as completed."""
    workout = await workout_repo.get(db, workout_id)
    if not workout or workout.member_id != member_id:
        raise ResourceNotFoundException("Workout not found")

    workout.completed = True
    workout.end_time = datetime.utcnow()
    if calories_burned:
        workout.calories_burned = calories_burned

    # Award points and achievements
    from backend.services.gamification_service import gamification_service
    await gamification_service.process_workout_completion(db, member_id, workout)

    db.add(workout)
    await db.commit()
    await db.refresh(workout)

    return WorkoutResponse.model_validate(workout)


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    member_id: int,
    workout_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a workout."""
    workout = await workout_repo.get(db, workout_id)
    if not workout or workout.member_id != member_id:
        raise ResourceNotFoundException("Workout not found")

    await db.delete(workout)
    await db.commit()
