from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models import User, Gym, Member, Trainer, Workout, Exercise
from backend.repositories.base import BaseRepository
from backend.schemas import UserRegisterRequest, GymCreateRequest


class UserRepository(BaseRepository[User, UserRegisterRequest, dict]):
    """User repository for database operations."""

    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_active_users(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        """Get all active users."""
        result = await db.execute(
            select(User).where(User.is_active == True).offset(skip).limit(limit)
        )
        users = result.scalars().all()

        count_result = await db.execute(select(User).where(User.is_active == True))
        total = len(count_result.scalars().all())

        return users, total


class GymRepository(BaseRepository[Gym, GymCreateRequest, dict]):
    """Gym repository for database operations."""

    def __init__(self):
        super().__init__(Gym)

    async def get_by_slug(self, db: AsyncSession, slug: str) -> Optional[Gym]:
        """Get gym by slug."""
        result = await db.execute(select(Gym).where(Gym.slug == slug))
        return result.scalars().first()

    async def get_by_owner(self, db: AsyncSession, owner_id: int) -> list[Gym]:
        """Get all gyms owned by a user."""
        result = await db.execute(select(Gym).where(Gym.owner_id == owner_id))
        return result.scalars().all()


class MemberRepository(BaseRepository[Member, dict, dict]):
    """Member repository for database operations."""

    def __init__(self):
        super().__init__(Member)

    async def get_by_user_and_gym(self, db: AsyncSession, user_id: int, gym_id: int) -> Optional[Member]:
        """Get member by user and gym."""
        result = await db.execute(
            select(Member).where((Member.user_id == user_id) & (Member.gym_id == gym_id))
        )
        return result.scalars().first()

    async def get_gym_members(self, db: AsyncSession, gym_id: int, active_only: bool = True) -> list[Member]:
        """Get all members of a gym."""
        query = select(Member).where(Member.gym_id == gym_id)
        if active_only:
            query = query.where(Member.is_active == True)
        result = await db.execute(query)
        return result.scalars().all()


class TrainerRepository(BaseRepository[Trainer, dict, dict]):
    """Trainer repository for database operations."""

    def __init__(self):
        super().__init__(Trainer)

    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> Optional[Trainer]:
        """Get trainer by user ID."""
        result = await db.execute(select(Trainer).where(Trainer.user_id == user_id))
        return result.scalars().first()

    async def get_gym_trainers(self, db: AsyncSession, gym_id: int) -> list[Trainer]:
        """Get all trainers in a gym."""
        result = await db.execute(select(Trainer).where(Trainer.gym_id == gym_id))
        return result.scalars().all()


class WorkoutRepository(BaseRepository[Workout, dict, dict]):
    """Workout repository for database operations."""

    def __init__(self):
        super().__init__(Workout)

    async def get_member_workouts(self, db: AsyncSession, member_id: int, limit: int = 50) -> list[Workout]:
        """Get recent workouts for a member."""
        result = await db.execute(
            select(Workout)
            .where(Workout.member_id == member_id)
            .order_by(Workout.start_time.desc())
            .limit(limit)
        )
        return result.scalars().all()


class ExerciseRepository(BaseRepository[Exercise, dict, dict]):
    """Exercise repository for database operations."""

    def __init__(self):
        super().__init__(Exercise)

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Exercise]:
        """Get exercise by name."""
        result = await db.execute(select(Exercise).where(Exercise.name == name))
        return result.scalars().first()

    async def get_active_exercises(self, db: AsyncSession) -> list[Exercise]:
        """Get all active exercises."""
        result = await db.execute(select(Exercise).where(Exercise.is_active == True))
        return result.scalars().all()
