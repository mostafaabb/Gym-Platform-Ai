from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db, get_current_user, get_current_admin
from app.core.rbac import require_role, PermissionChecker, SUPER_ADMIN, GYM_OWNER, TRAINER, MEMBER, ALL_ROLES
from db.models import User, UserRole

router = APIRouter(prefix="/users", tags=["users"])


class UserProfile(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    age: int | None
    weight_kg: float | None
    height_cm: float | None
    email_verified: bool
    recovery_score: float
    created_at: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: str | None = None
    age: int | None = None
    weight_kg: float | None = None
    height_cm: float | None = None
    preferences: dict | None = None


class UserListResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    created_at: str


@router.get("/me", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfile.from_orm(current_user)


@router.put("/me", response_model=UserProfile)
async def update_profile(
    request: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user profile"""
    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if request.full_name:
        user.full_name = request.full_name
    if request.age is not None:
        user.age = request.age
    if request.weight_kg is not None:
        user.weight_kg = request.weight_kg
    if request.height_cm is not None:
        user.height_cm = request.height_cm
    if request.preferences is not None:
        user.preferences = request.preferences

    db.commit()
    db.refresh(user)
    return UserProfile.from_orm(user)


@router.get("", response_model=list[UserListResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role: UserRole | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List users (admin only)"""
    if current_user.role != UserRole.super_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    query = db.query(User)

    if role:
        query = query.filter(User.role == role)

    users = query.offset(skip).limit(limit).all()
    return [UserListResponse.from_orm(u) for u in users]


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete user (admin or self)"""
    if current_user.id != user_id and current_user.role != UserRole.super_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own account")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()
