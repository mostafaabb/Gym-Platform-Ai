import asyncio
import logging
from backend.core.database import init_db, get_db, engine
from backend.models import User, RoleEnum, Gym, SubscriptionPlanEnum
from backend.core.security import hash_password
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_data():
    async with AsyncSession(engine) as session:
        # Check if super admin exists
        result = await session.execute(select(User).where(User.email == "admin@gymflow.ai"))
        admin = result.scalars().first()
        
        if not admin:
            logger.info("Creating super admin...")
            admin = User(
                email="admin@gymflow.ai",
                password_hash=hash_password("admin123"),
                first_name="Super",
                last_name="Admin",
                role=RoleEnum.SUPER_ADMIN,
                is_active=True,
                is_verified=True
            )
            session.add(admin)
            await session.commit()
            await session.refresh(admin)
            logger.info("Super admin created.")

        # Check if test gym exists
        # Fix query: select by name
        result = await session.execute(select(Gym).where(Gym.name == "Iron Paradise"))
        gym = result.scalars().first()
        
        if not gym:
            logger.info("Creating test gym...")
            gym = Gym(
                owner_id=admin.id,
                name="Iron Paradise",
                slug="iron-paradise",
                email="info@ironparadise.com",
                phone="1234567890",
                address="123 Muscle Beach",
                city="Venice",
                state="CA",
                country="USA",
                postal_code="90291",
                subscription_plan=SubscriptionPlanEnum.ENTERPRISE,
                is_active=True
            )
            session.add(gym)
            await session.commit()
            logger.info("Test gym created.")

async def main():
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized.")
    await seed_data()
    logger.info("Seed data completed.")

if __name__ == "__main__":
    asyncio.run(main())
