import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.models import Gym, User, Trainer, Member, Membership, RoleEnum
from backend.schemas import GymCreate, GymUpdate

logger = logging.getLogger(__name__)

class GymService:
    @staticmethod
    async def create_gym(db: AsyncSession, owner_id: int, gym_data: GymCreate) -> Gym:
        """Create a new gym and assign the owner."""
        gym = Gym(
            owner_id=owner_id,
            name=gym_data.name,
            slug=gym_data.name.lower().replace(" ", "-"),
            email=gym_data.email,
            phone=gym_data.phone,
            address=gym_data.address,
            city=gym_data.city,
            state=gym_data.state,
            country=gym_data.country,
            postal_code=gym_data.postal_code,
        )
        db.add(gym)
        await db.commit()
        await db.refresh(gym)
        return gym

    @staticmethod
    async def get_gym_analytics(db: AsyncSession, gym_id: int):
        """Calculate gym-wide analytics (revenue, members, attendance)."""
        # Member count
        member_count = await db.scalar(
            select(func.count(Member.id)).where(Member.gym_id == gym_id)
        )
        
        # Trainer count
        trainer_count = await db.scalar(
            select(func.count(Trainer.id)).where(Trainer.gym_id == gym_id)
        )
        
        # This is a simplified version of revenue calculation
        total_revenue = await db.scalar(
            select(func.sum(Membership.price)).where(Membership.gym_id == gym_id)
        ) or 0.0

        return {
            "member_count": member_count,
            "trainer_count": trainer_count,
            "total_revenue": float(total_revenue),
            "retention_rate": 95.0, # Placeholder
            "peak_hours": [18, 19, 20] # Placeholder
        }

    @staticmethod
    async def add_trainer_to_gym(db: AsyncSession, gym_id: int, user_id: int):
        """Onboard a new trainer to a specific gym."""
        trainer = Trainer(
            user_id=user_id,
            gym_id=gym_id,
            is_active=True
        )
        db.add(trainer)
        
        # Update user role to trainer
        user = await db.get(User, user_id)
        if user:
            user.role = RoleEnum.TRAINER
            
        await db.commit()
        return trainer

    @staticmethod
    async def get_gym_members(db: AsyncSession, gym_id: int):
        """List all members associated with a gym."""
        result = await db.execute(
            select(Member).where(Member.gym_id == gym_id)
        )
        return result.scalars().all()

gym_service = GymService()
