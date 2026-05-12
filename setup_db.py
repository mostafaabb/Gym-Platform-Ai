import sys
import os
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from db.session import engine, SessionLocal
from db.base import Base
from db.models import User, Gym, Membership, MembershipStatus

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def setup():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if user already exists
        user = db.query(User).filter(User.email == "test@example.com").first()
        if not user:
            print("Creating test user...")
            hashed_password = pwd_context.hash("password123")
            user = User(
                email="test@example.com",
                full_name="Test User",
                hashed_password=hashed_password,
                age=30,
                weight_kg=80.0
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"User {user.email} created.")
        else:
            print(f"User {user.email} already exists.")

        # Create a test gym
        gym = db.query(Gym).filter(Gym.name == "Iron Paradise").first()
        if not gym:
            print("Creating test gym...")
            gym = Gym(
                name="Iron Paradise",
                location="Muscle Beach",
                owner_email="owner@example.com"
            )
            db.add(gym)
            db.commit()
            db.refresh(gym)
            print(f"Gym {gym.name} created.")
        
        # Create membership
        membership = db.query(Membership).filter(Membership.user_id == user.id, Membership.gym_id == gym.id).first()
        if not membership:
            print("Creating membership...")
            membership = Membership(
                user_id=user.id,
                gym_id=gym.id,
                status=MembershipStatus.active
            )
            db.add(membership)
            db.commit()
            print("Membership created.")
            
    finally:
        db.close()

if __name__ == "__main__":
    setup()
