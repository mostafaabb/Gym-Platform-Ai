from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.exceptions import AuthenticationException, AuthorizationException
from backend.core.security import decode_token
from backend.models import RoleEnum, User
from backend.repositories.repositories import UserRepository


ROLE_PERMISSIONS: dict[RoleEnum, set[str]] = {
    RoleEnum.SUPER_ADMIN: {
        "system:manage",
        "gyms:manage",
        "users:manage",
        "billing:manage",
        "analytics:view",
        "reports:manage",
        "ai:use",
        "workouts:manage",
        "nutrition:manage",
        "messages:send",
    },
    RoleEnum.GYM_OWNER: {
        "gyms:manage",
        "members:manage",
        "trainers:manage",
        "billing:manage",
        "analytics:view",
        "reports:manage",
        "ai:use",
        "messages:send",
    },
    RoleEnum.TRAINER: {
        "members:view",
        "workouts:manage",
        "analytics:view",
        "ai:use",
        "nutrition:manage",
        "messages:send",
    },
    RoleEnum.MEMBER: {
        "workouts:self",
        "nutrition:self",
        "analytics:self",
        "ai:use",
        "messages:send",
    },
}


user_repo = UserRepository()


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AuthenticationException("Missing access token")

    try:
        payload = decode_token(authorization.split(" ", 1)[1])
    except ValueError as exc:
        raise AuthenticationException(str(exc)) from exc

    if payload.get("type") != "access":
        raise AuthenticationException("Invalid access token")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationException("Invalid access token subject")

    user = await user_repo.get(db, int(user_id))
    if not user or not user.is_active:
        raise AuthenticationException("User account is inactive")

    return user


def has_permission(role: RoleEnum, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())


def require_roles(*roles: RoleEnum) -> Callable:
    async def _dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise AuthorizationException("This role cannot access the requested resource")
        return user

    return _dependency


def require_permissions(*permissions: str) -> Callable:
    async def _dependency(user: User = Depends(get_current_user)) -> User:
        granted = ROLE_PERMISSIONS.get(user.role, set())
        if not set(permissions).issubset(granted):
            raise AuthorizationException("Insufficient permissions")
        return user

    return _dependency


def role_payload(user: User) -> dict[str, object]:
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role.value,
        "permissions": sorted(ROLE_PERMISSIONS.get(user.role, set())),
    }
