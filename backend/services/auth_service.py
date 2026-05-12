import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.config import get_settings
from backend.models import User
from backend.schemas import RoleEnum

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_tokens(user_id: int, role: RoleEnum) -> dict:
        """Create access and refresh tokens."""
        access_token = AuthService._create_access_token(
            data={"sub": str(user_id), "role": role},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = AuthService._create_refresh_token(
            data={"sub": str(user_id), "role": role},
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    def _create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def _create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Decode JWT token."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None

    @staticmethod
    async def get_current_user(db: AsyncSession, token: str) -> Optional[User]:
        """Get current user from token."""
        payload = AuthService.decode_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        stmt = select(User).where(User.id == int(user_id))
        result = await db.execute(stmt)
        user = result.scalars().first()
        return user


class RBACService:
    """Role-based access control service."""

    PERMISSIONS = {
        RoleEnum.SUPER_ADMIN: [
            "manage_system",
            "manage_gyms",
            "manage_users",
            "manage_subscriptions",
            "view_analytics",
            "manage_settings"
        ],
        RoleEnum.GYM_OWNER: [
            "manage_gym",
            "manage_trainers",
            "manage_members",
            "view_gym_analytics",
            "manage_billing"
        ],
        RoleEnum.TRAINER: [
            "view_clients",
            "manage_sessions",
            "view_progress",
            "send_notifications"
        ],
        RoleEnum.MEMBER: [
            "view_profile",
            "track_workouts",
            "use_ai_coach",
            "view_progress",
            "access_nutrition"
        ]
    }

    @staticmethod
    def has_permission(role: RoleEnum, permission: str) -> bool:
        """Check if role has permission."""
        permissions = RBACService.PERMISSIONS.get(role, [])
        return permission in permissions

    @staticmethod
    def has_any_permission(role: RoleEnum, permissions: list) -> bool:
        """Check if role has any of the permissions."""
        return any(RBACService.has_permission(role, perm) for perm in permissions)

    @staticmethod
    def has_all_permissions(role: RoleEnum, permissions: list) -> bool:
        """Check if role has all permissions."""
        return all(RBACService.has_permission(role, perm) for perm in permissions)
