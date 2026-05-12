from typing import Callable
from functools import wraps

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from db.models import User, UserRole


def get_current_user_from_db(user: User, db: Session) -> User:
    """Fetch fresh user from database"""
    return db.query(User).filter(User.id == user.id).first()


def require_role(*roles: UserRole):
    """Decorator to check user role"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user: User = None, db: Session = Depends(get_db), **kwargs):
            if current_user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

            fresh_user = get_current_user_from_db(current_user, db)
            if fresh_user.role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"This action requires one of these roles: {', '.join([r.value for r in roles])}"
                )
            return await func(*args, current_user=fresh_user, db=db, **kwargs)
        return wrapper
    return decorator


class PermissionChecker:
    """Check permissions based on user role and resource ownership"""

    @staticmethod
    def can_manage_gym(user: User, gym_id: int, db: Session) -> bool:
        """Check if user can manage gym"""
        if user.role == UserRole.super_admin:
            return True
        if user.role == UserRole.gym_owner:
            from db.models import Gym
            gym = db.query(Gym).filter(Gym.id == gym_id).first()
            return gym and gym.owner_email == user.email
        return False

    @staticmethod
    def can_manage_member(user: User, member_id: int, db: Session) -> bool:
        """Check if user can manage member"""
        if user.role == UserRole.super_admin:
            return True
        if user.role == UserRole.member and user.id == member_id:
            return True
        if user.role == UserRole.trainer:
            from db.models import Membership
            member = db.query(User).filter(User.id == member_id).first()
            if member:
                membership = db.query(Membership).filter(
                    Membership.user_id == member_id
                ).first()
                trainer = db.query(User).filter(User.id == user.id).first()
                if trainer.trainer_profile:
                    return membership.gym_id == trainer.trainer_profile.gym_id
        return False

    @staticmethod
    def can_access_resource(user: User, resource_owner_id: int) -> bool:
        """Check if user can access resource"""
        if user.role == UserRole.super_admin:
            return True
        return user.id == resource_owner_id


def check_permission(permission_func: Callable):
    """Generic permission checker decorator"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user: User = None, **kwargs):
            if current_user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

            if not permission_func(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to access this resource"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


# Role constants for easier use
SUPER_ADMIN = UserRole.super_admin
GYM_OWNER = UserRole.gym_owner
TRAINER = UserRole.trainer
MEMBER = UserRole.member
ALL_ROLES = [SUPER_ADMIN, GYM_OWNER, TRAINER, MEMBER]
