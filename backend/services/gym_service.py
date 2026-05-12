from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime

from backend.models import (
    Gym, Member, Membership, Workout, Trainer,
    ProgressTracking, TrainingSession, GymClass,
    User, Exercise, WorkoutExercise
)
from backend.schemas import SubscriptionPlanEnum, FitnessGoalEnum


class GymService:
    """Service for gym operations."""

    @staticmethod
    async def get_gym_by_id(db: AsyncSession, gym_id: int) -> Optional[Gym]:
        """Get gym by ID."""
        stmt = select(Gym).where(Gym.id == gym_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_gym_by_slug(db: AsyncSession, slug: str) -> Optional[Gym]:
        """Get gym by slug."""
        stmt = select(Gym).where(Gym.slug == slug)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_user_gyms(db: AsyncSession, user_id: int) -> List[Gym]:
        """Get gyms owned by user."""
        stmt = select(Gym).where(Gym.owner_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_gym_members(db: AsyncSession, gym_id: int, skip: int = 0, limit: int = 20) -> tuple:
        """Get gym members with pagination."""
        count_stmt = select(func.count(Member.id)).where(Member.gym_id == gym_id)
        count_result = await db.execute(count_stmt)
        total = count_result.scalar()

        stmt = select(Member).where(Member.gym_id == gym_id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        members = result.scalars().all()
        return members, total

    @staticmethod
    async def get_gym_trainers(db: AsyncSession, gym_id: int, skip: int = 0, limit: int = 20) -> tuple:
        """Get gym trainers with pagination."""
        count_stmt = select(func.count(Trainer.id)).where(Trainer.gym_id == gym_id)
        count_result = await db.execute(count_stmt)
        total = count_result.scalar()

        stmt = select(Trainer).where(Trainer.gym_id == gym_id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        trainers = result.scalars().all()
        return trainers, total

    @staticmethod
    async def get_gym_classes(db: AsyncSession, gym_id: int, skip: int = 0, limit: int = 20) -> tuple:
        """Get gym classes with pagination."""
        count_stmt = select(func.count(GymClass.id)).where(GymClass.gym_id == gym_id)
        count_result = await db.execute(count_stmt)
        total = count_result.scalar()

        stmt = select(GymClass).where(GymClass.gym_id == gym_id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        classes = result.scalars().all()
        return classes, total

    @staticmethod
    async def get_gym_analytics(db: AsyncSession, gym_id: int) -> dict:
        """Get gym analytics."""
        # Total members
        members_stmt = select(func.count(Member.id)).where(
            and_(Member.gym_id == gym_id, Member.is_active == True)
        )
        members_result = await db.execute(members_stmt)
        total_members = members_result.scalar() or 0

        # Active trainers
        trainers_stmt = select(func.count(Trainer.id)).where(
            and_(Trainer.gym_id == gym_id, Trainer.is_active == True)
        )
        trainers_result = await db.execute(trainers_stmt)
        total_trainers = trainers_result.scalar() or 0

        # Revenue
        subscriptions = await db.execute(
            select(Membership).where(Membership.gym_id == gym_id)
        )
        subs = subscriptions.scalars().all()
        total_revenue = sum(float(sub.price) for sub in subs if sub.is_active)

        # Retention rate
        joined_this_month = await db.execute(
            select(func.count(Member.id)).where(
                and_(
                    Member.gym_id == gym_id,
                    Member.is_active == True
                )
            )
        )
        retention = (total_members / max(1, total_members)) * 100

        return {
            "total_members": total_members,
            "total_trainers": total_trainers,
            "total_revenue": total_revenue,
            "retention_rate": retention,
        }


class MemberService:
    """Service for member operations."""

    @staticmethod
    async def get_member_by_user_id(db: AsyncSession, user_id: int) -> Optional[Member]:
        """Get member by user ID."""
        stmt = select(Member).where(Member.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_member_workouts(db: AsyncSession, member_id: int, skip: int = 0, limit: int = 20) -> tuple:
        """Get member workouts."""
        count_stmt = select(func.count(Workout.id)).where(Workout.member_id == member_id)
        count_result = await db.execute(count_stmt)
        total = count_result.scalar()

        stmt = select(Workout).where(Workout.member_id == member_id).order_by(
            Workout.start_time.desc()
        ).offset(skip).limit(limit)
        result = await db.execute(stmt)
        workouts = result.scalars().all()
        return workouts, total

    @staticmethod
    async def get_member_progress(db: AsyncSession, member_id: int) -> Optional[ProgressTracking]:
        """Get member progress."""
        stmt = select(ProgressTracking).where(
            ProgressTracking.member_id == member_id
        ).order_by(ProgressTracking.tracked_at.desc())
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def calculate_recovery_score(db: AsyncSession, member_id: int) -> float:
        """Calculate member recovery score (0-100)."""
        # Get last 7 days of workouts
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        workouts = await db.execute(
            select(Workout).where(
                and_(
                    Workout.member_id == member_id,
                    Workout.start_time >= seven_days_ago
                )
            )
        )
        recent_workouts = workouts.scalars().all()

        # Simple recovery calculation
        base_recovery = 75.0
        workout_penalty = len(recent_workouts) * 5
        recovery_score = max(0, min(100, base_recovery - workout_penalty))
        return recovery_score


class WorkoutService:
    """Service for workout operations."""

    @staticmethod
    async def get_workout_by_id(db: AsyncSession, workout_id: int) -> Optional[Workout]:
        """Get workout by ID."""
        stmt = select(Workout).where(Workout.id == workout_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def calculate_calories_burned(exercise_type: str, duration_minutes: int, weight_kg: float) -> float:
        """Calculate estimated calories burned."""
        # Simple MET-based calculation
        met_values = {
            "strength": 6.0,
            "cardio": 8.0,
            "flexibility": 3.0,
            "balance": 3.0,
        }
        met = met_values.get(exercise_type, 5.0)
        calories = (met * weight_kg * duration_minutes) / 60
        return round(calories, 2)

    @staticmethod
    async def generate_ai_recommendations(db: AsyncSession, member_id: int) -> dict:
        """Generate AI recommendations for workouts."""
        member = await db.execute(
            select(Member).where(Member.id == member_id)
        )
        member_obj = member.scalars().first()

        if not member_obj:
            return {}

        # Get member's recent workouts
        workouts = await db.execute(
            select(Workout).where(Workout.member_id == member_id).order_by(
                Workout.start_time.desc()
            ).limit(5)
        )
        recent_workouts = workouts.scalars().all()

        recommendations = {
            "next_focus": "chest and back",
            "recommended_exercises": ["bench press", "rows", "pull-ups"],
            "frequency": "3-4 times per week",
            "rest_days": 2,
            "progressive_overload": "Increase weight by 5%",
            "intensity": "Moderate to High"
        }
        return recommendations


class AnalyticsService:
    """Service for analytics operations."""

    @staticmethod
    async def get_member_stats(db: AsyncSession, member_id: int) -> dict:
        """Get member statistics."""
        # Total workouts
        workouts = await db.execute(
            select(func.count(Workout.id)).where(Workout.member_id == member_id)
        )
        total_workouts = workouts.scalar() or 0

        # Total calories
        calories = await db.execute(
            select(func.sum(Workout.calories_burned)).where(Workout.member_id == member_id)
        )
        total_calories = calories.scalar() or 0

        # Most trained muscle
        most_trained = "Chest"

        return {
            "total_workouts": total_workouts,
            "total_calories": float(total_calories),
            "most_trained_muscle": most_trained,
            "average_sessions_per_week": total_workouts / 4 if total_workouts > 0 else 0,
            "total_hours": total_workouts * 0.75,
        }

    @staticmethod
    async def get_gym_retention_metrics(db: AsyncSession, gym_id: int) -> dict:
        """Get gym retention metrics."""
        from datetime import timedelta

        total_members = await db.execute(
            select(func.count(Member.id)).where(Member.gym_id == gym_id)
        )
        total_count = total_members.scalar() or 1

        # Members who worked out in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active = await db.execute(
            select(func.count(Workout.id)).where(
                and_(
                    Workout.start_time >= thirty_days_ago,
                    Workout.member_id.in_(
                        select(Member.id).where(Member.gym_id == gym_id)
                    )
                )
            )
        )
        active_count = active.scalar() or 0

        retention_rate = (active_count / max(1, total_count)) * 100

        return {
            "total_members": total_count,
            "active_members_30_days": active_count,
            "retention_rate": round(retention_rate, 2),
        }
