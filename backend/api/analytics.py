from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from backend.core.database import get_db
from backend.core.exceptions import ResourceNotFoundException
from backend.models import Workout, Member, ProgressTracking, NutritionLog, Attendance
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


@router.get("/owners/churn-risk/{gym_id}")
async def get_at_risk_members(gym_id: int, db: AsyncSession = Depends(get_db)):
    """Identifies members belonging to a gym whose activity baseline has plummeted, predicting churn."""
    now = datetime.utcnow()
    two_weeks_ago = now - timedelta(days=14)
    
    # Query all active members in the gym
    query = select(Member).where(
        Member.gym_id == gym_id,
        Member.is_active == True
    )
    result = await db.execute(query)
    members = result.scalars().all()
    
    at_risk_list = []
    
    for member in members:
        # Load user context if available
        user_result = await db.execute(select(Member).where(Member.id == member.id))
        
        # 1. Fetch attendance check-in count
        att_query = select(func.count(Attendance.id)).where(
            Attendance.member_id == member.id,
            Attendance.check_in_at >= two_weeks_ago
        )
        att_result = await db.execute(att_query)
        check_ins = att_result.scalar() or 0
        
        # 2. Fetch workout count in last 14 days
        workout_query = select(func.count(Workout.id)).where(
            Workout.member_id == member.id,
            Workout.start_time >= two_weeks_ago,
            Workout.completed == True
        )
        workout_result = await db.execute(workout_query)
        workouts = workout_result.scalar() or 0
        
        # 3. Calculate Risk Index (w1 * attendance drop + w2 * workout drop)
        # Assuming standard benchmark is 4 check-ins and 4 workouts in 2 weeks
        att_score = min(100, (check_ins / 4) * 100)
        workout_score = min(100, (workouts / 4) * 100)
        
        # 100 is fully consistent, 0 is fully lapsed
        consistency = (0.5 * att_score) + (0.5 * workout_score)
        churn_prob = round(100 - consistency, 1)
        
        # If churn risk is above 40%, flag it
        if churn_prob >= 40.0:
            at_risk_list.append({
                "member_id": member.id,
                "check_ins_14d": check_ins,
                "workouts_14d": workouts,
                "churn_probability": churn_prob,
                "risk_tier": "Critical" if churn_prob >= 75 else "Warning",
                "recommended_action": "Send 1-on-1 Trainer Session Voucher"
            })
            
    return {
        "gym_id": gym_id,
        "total_at_risk_members": len(at_risk_list),
        "at_risk_members": sorted(at_risk_list, key=lambda x: x["churn_probability"], reverse=True)
    }


@router.get("/members/{member_id}/muscle-recovery")
async def get_muscle_recovery(member_id: int, db: AsyncSession = Depends(get_db)):
    """Calculates dynamic muscle recovery percentage based on a biological decay formula."""
    now = datetime.utcnow()
    
    # Fetch all completed workouts in last 7 days
    result = await db.execute(
        select(Workout)
        .where(
            Workout.member_id == member_id,
            Workout.completed == True,
            Workout.start_time >= now - timedelta(days=7)
        )
        .order_by(Workout.start_time.desc())
    )
    recent_workouts = result.scalars().all()
    
    # Core muscle groups
    muscle_groups = ["Chest", "Quads", "Triceps", "Back", "Shoulders", "Hamstrings", "Biceps"]
    last_trained = {}
    
    for workout in recent_workouts:
        w_type = workout.workout_type or "general"
        # Map workout types to target muscle groups
        targets = []
        if "chest" in w_type.lower() or "push" in w_type.lower():
            targets.extend(["Chest", "Triceps", "Shoulders"])
        if "back" in w_type.lower() or "pull" in w_type.lower():
            targets.extend(["Back", "Biceps"])
        if "leg" in w_type.lower() or "squat" in w_type.lower():
            targets.extend(["Quads", "Hamstrings"])
            
        for m in targets:
            if m not in last_trained:
                last_trained[m] = workout.start_time
                
    recovery_data = []
    # Biological decay constant (30 hour half-life: lambda = 0.023)
    lam = 0.023
    
    for m in muscle_groups:
        if m in last_trained:
            hours_since = (now - last_trained[m]).total_seconds() / 3600
            # Recovery starts at 20% immediately post-workout and recovers exponentially
            rec = 20.0 + (100.0 - 20.0) * (1.0 - __import__('math').exp(-lam * hours_since))
            rec = round(min(100.0, rec), 1)
            time_str = f"{round(hours_since, 1)} hours ago"
        else:
            rec = 100.0
            time_str = "more than 7 days ago"
            
        recovery_data.append({
            "name": m,
            "recovery": rec,
            "lastTrained": time_str
        })
        
    return recovery_data

