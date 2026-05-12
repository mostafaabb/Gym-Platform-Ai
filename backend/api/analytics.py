from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from backend.core.database import get_db
from backend.core.exceptions import ResourceNotFoundException
from backend.models import Workout, Member, ProgressTracking, NutritionLog
from backend.schemas import WorkoutStatsResponse, MemberAnalyticsResponse, GymAnalyticsResponse
from backend.repositories.repositories import MemberRepository

router = APIRouter(prefix="/analytics", tags=["Analytics"])
member_repo = MemberRepository()


@router.get("/members/{member_id}", response_model=MemberAnalyticsResponse)
async def get_member_analytics(
    member_id: int,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get member analytics and progress."""
    member = await member_repo.get(db, member_id)
    if not member:
        raise ResourceNotFoundException("Member not found")

    # Calculate date range
    now = datetime.utcnow()
    start_date = now - timedelta(days=days)

    # Get workouts
    result = await db.execute(
        select(Workout).where(
            (Workout.member_id == member_id) &
            (Workout.start_time >= start_date)
        )
    )
    workouts = result.scalars().all()

    # Calculate stats
    total_workouts = len([w for w in workouts if w.completed])
    total_hours = sum(w.duration_minutes for w in workouts) / 60 if workouts else 0
    total_calories = sum(w.calories_burned or 0 for w in workouts)
    avg_sessions_per_week = total_workouts / (days / 7) if days > 0 else 0

    # Get most trained muscle (from exercise types)
    from collections import Counter
    muscle_groups = []
    for workout in workouts:
        # This is simplified - in production, you'd track muscle groups properly
        muscle_groups.append(workout.workout_type or "general")

    most_trained = Counter(muscle_groups).most_common(1)[0][0] if muscle_groups else None

    # Get progress
    result = await db.execute(
        select(ProgressTracking)
        .where(ProgressTracking.member_id == member_id)
        .order_by(ProgressTracking.tracked_at.desc())
        .limit(1)
    )
    latest_progress = result.scalars().first()

    # Get last workout
    result = await db.execute(
        select(Workout)
        .where(Workout.member_id == member_id)
        .order_by(Workout.start_time.desc())
        .limit(1)
    )
    last_workout = result.scalars().first()

    return MemberAnalyticsResponse(
        member_id=member_id,
        stats=WorkoutStatsResponse(
            total_workouts=total_workouts,
            total_hours=total_hours,
            total_calories=total_calories,
            average_sessions_per_week=avg_sessions_per_week,
            most_trained_muscle=most_trained,
        ),
        progress=latest_progress,
        goals=[member.fitness_goal] if member.fitness_goal else [],
        last_workout=last_workout.start_time if last_workout else None,
    )


@router.get("/gyms/{gym_id}", response_model=GymAnalyticsResponse)
async def get_gym_analytics(
    gym_id: int,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get gym analytics and metrics."""
    # Get member count
    result = await db.execute(
        select(func.count(Member.id)).where(Member.gym_id == gym_id)
    )
    total_members = result.scalar() or 0

    # Get active members
    result = await db.execute(
        select(func.count(Member.id)).where(
            (Member.gym_id == gym_id) & (Member.is_active == True)
        )
    )
    active_members = result.scalar() or 0

    # Calculate stats
    member_retention_rate = (active_members / total_members * 100) if total_members > 0 else 0

    return GymAnalyticsResponse(
        gym_id=gym_id,
        total_members=total_members,
        active_members=active_members,
        total_trainers=0,  # TODO: Calculate from trainers table
        subscription_revenue=0.0,  # TODO: Calculate from subscriptions
        member_retention_rate=member_retention_rate,
        peak_hours=[],  # TODO: Calculate from attendance data
    )


@router.get("/members/{member_id}/progress")
async def get_member_progress(
    member_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get member progress over time."""
    member = await member_repo.get(db, member_id)
    if not member:
        raise ResourceNotFoundException("Member not found")

    result = await db.execute(
        select(ProgressTracking)
        .where(ProgressTracking.member_id == member_id)
        .order_by(ProgressTracking.tracked_at)
    )
    progress = result.scalars().all()

    return {
        "member_id": member_id,
        "progress_history": [
            {
                "date": p.tracked_at,
                "weight_kg": p.weight_kg,
                "body_fat_percentage": p.body_fat_percentage,
                "muscle_mass_kg": p.muscle_mass_kg,
                "recovery_score": p.recovery_score,
            }
            for p in progress
        ]
    }


@router.get("/members/{member_id}/nutrition")
async def get_member_nutrition_summary(
    member_id: int,
    days: int = Query(7, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get member nutrition summary."""
    start_date = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(NutritionLog)
        .where(
            (NutritionLog.member_id == member_id) &
            (NutritionLog.logged_at >= start_date)
        )
        .order_by(NutritionLog.logged_at.desc())
    )
    logs = result.scalars().all()

    avg_calories = sum(l.total_calories or 0 for l in logs) / len(logs) if logs else 0
    avg_protein = sum(l.protein_g or 0 for l in logs) / len(logs) if logs else 0
    avg_carbs = sum(l.carbs_g or 0 for l in logs) / len(logs) if logs else 0
    avg_fat = sum(l.fat_g or 0 for l in logs) / len(logs) if logs else 0

    return {
        "member_id": member_id,
        "days": days,
        "entries_count": len(logs),
        "averages": {
            "daily_calories": avg_calories,
            "protein_g": avg_protein,
            "carbs_g": avg_carbs,
            "fat_g": avg_fat,
        },
        "recent_entries": [
            {
                "date": l.logged_at,
                "meal_type": l.meal_type,
                "calories": l.total_calories,
            }
            for l in logs[:10]
        ]
    }
