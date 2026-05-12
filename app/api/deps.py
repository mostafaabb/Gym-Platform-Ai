from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session

from app.core.auth import verify_token
from db.models import User
from db.session import SessionLocal

security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials

    token_data = verify_token(token, token_type="access")
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(token_data.sub)
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Get current admin user"""
    from db.models import UserRole

    if current_user.role != UserRole.super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
