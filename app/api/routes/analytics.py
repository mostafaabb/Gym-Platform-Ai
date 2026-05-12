from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user
from db.models import User, Workout, WorkoutLog, FoodLog

router = APIRouter(prefix="/analytics", tags=["analytics"])


class ProgressStats(BaseModel):
    total_workouts: int
    total_exercises: int
    calories_burned_week: float
    avg_workout_duration: float
    consistency_score: float
    recovery_score: float


class WorkoutMetrics(BaseModel):
    date: str
    workouts_count: int
    total_duration_minutes: int
    exercises_count: int
    calories_burned: float


@router.get("/progress", response_model=ProgressStats)
async def get_progress_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user progress statistics"""
    start_date = datetime.utcnow() - timedelta(days=days)

    workouts = db.query(Workout).filter(
        Workout.user_id == current_user.id,
        Workout.created_at >= start_date
    ).all()

    exercises = db.query(WorkoutLog).filter(
        WorkoutLog.logged_at >= start_date
    ).count()

    total_workouts = len(workouts)
    avg_duration = sum(
        (w.completed_at - w.started_at).total_seconds() / 60
        for w in workouts if w.completed_at
    ) / max(total_workouts, 1)

    consistency = min(100, (total_workouts / (days / 7)) * 100) if days > 0 else 0

    return ProgressStats(
        total_workouts=total_workouts,
        total_exercises=exercises,
        calories_burned_week=0.0,
        avg_workout_duration=avg_duration,
        consistency_score=consistency,
        recovery_score=current_user.recovery_score,
    )


@router.get("/workout-metrics", response_model=list[WorkoutMetrics])
async def get_workout_metrics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get daily workout metrics"""
    start_date = datetime.utcnow() - timedelta(days=days)

    workouts = db.query(Workout).filter(
        Workout.user_id == current_user.id,
        Workout.started_at >= start_date
    ).all()

    metrics_dict = {}
    for workout in workouts:
        date_str = workout.started_at.date().isoformat()
        if date_str not in metrics_dict:
            metrics_dict[date_str] = {
                "workouts_count": 0,
                "total_duration_minutes": 0,
                "exercises_count": 0,
                "calories_burned": 0.0,
            }

        metrics_dict[date_str]["workouts_count"] += 1
        if workout.completed_at:
            duration = (workout.completed_at - workout.started_at).total_seconds() / 60
            metrics_dict[date_str]["total_duration_minutes"] += duration

    metrics = [
        WorkoutMetrics(date=date, **stats)
        for date, stats in sorted(metrics_dict.items())
    ]

    return metrics
