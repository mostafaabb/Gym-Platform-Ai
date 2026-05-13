from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import get_settings
from backend.core.database import get_db
from backend.core.exceptions import AuthenticationException, ConflictException, ResourceNotFoundException
from backend.core.rbac import get_current_user, role_payload
from backend.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from backend.models import RefreshToken, User
from backend.repositories.repositories import UserRepository
from backend.schemas import (
    EmailVerificationRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()
user_repo = UserRepository()


async def _persist_refresh_token(
    db: AsyncSession,
    *,
    user: User,
    token: str,
    request: Request | None = None,
    replaced_by: str | None = None,
) -> None:
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_token(token),
            replaced_by_token_hash=hash_token(replaced_by) if replaced_by else None,
            expires_at=expires_at,
            ip_address=request.headers.get("x-forwarded-for")
            if request
            else None,
            user_agent=request.headers.get("user-agent") if request else None,
        )
    )


def _issue_tokens(user: User) -> tuple[str, str]:
    claims = {"role": user.role.value, "email": user.email}
    return (
        create_access_token(user.id, extra_claims=claims),
        create_refresh_token(user.id, extra_claims=claims),
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    existing_user = await user_repo.get_by_email(db, payload.email)
    if existing_user:
        raise ConflictException("User with this email already exists")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        role=payload.role,
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await user_repo.get_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise AuthenticationException("Invalid email or password")
    if not user.is_active:
        raise AuthenticationException("User account is inactive")

    access_token, refresh_token = _issue_tokens(user)
    user.last_login = datetime.utcnow()
    await _persist_refresh_token(db, user=user, token=refresh_token, request=request)
    await db.commit()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: RefreshTokenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    try:
        token_payload = decode_token(payload.refresh_token)
    except ValueError as exc:
        raise AuthenticationException(str(exc)) from exc

    if token_payload.get("type") != "refresh":
        raise AuthenticationException("Invalid refresh token")

    token_digest = hash_token(payload.refresh_token)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_digest,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.utcnow(),
        )
    )
    stored_token = result.scalars().first()
    if not stored_token:
        raise AuthenticationException("Refresh token is invalid or revoked")

    user = await user_repo.get(db, int(token_payload["sub"]))
    if not user or not user.is_active:
        raise AuthenticationException("User account is inactive")

    access_token, new_refresh_token = _issue_tokens(user)
    stored_token.revoked_at = datetime.utcnow()
    stored_token.replaced_by_token_hash = hash_token(new_refresh_token)
    await _persist_refresh_token(
        db,
        user=user,
        token=new_refresh_token,
        request=request,
        replaced_by=payload.refresh_token,
    )
    await db.commit()
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return {
        "user": UserResponse.model_validate(user),
        "auth": role_payload(user),
    }


@router.post("/logout")
async def logout(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    token_digest = hash_token(payload.refresh_token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_digest))
    stored_token = result.scalars().first()
    if stored_token:
        stored_token.revoked_at = datetime.utcnow()
        await db.commit()
    return {"message": "Logged out successfully"}


@router.get("/sessions")
async def list_sessions(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RefreshToken)
        .where(RefreshToken.user_id == user.id)
        .order_by(RefreshToken.created_at.desc())
    )
    sessions = result.scalars().all()
    return {
        "items": [
            {
                "id": session.id,
                "device_label": session.device_label,
                "ip_address": session.ip_address,
                "user_agent": session.user_agent,
                "created_at": session.created_at,
                "expires_at": session.expires_at,
                "revoked_at": session.revoked_at,
                "active": session.revoked_at is None and session.expires_at > datetime.utcnow(),
            }
            for session in sessions
        ]
    }


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_session(
    session_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await db.get(RefreshToken, session_id)
    if not session or session.user_id != user.id:
        raise ResourceNotFoundException("Session not found")
    session.revoked_at = datetime.utcnow()
    await db.commit()


@router.post("/forgot-password")
async def forgot_password(payload: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    await user_repo.get_by_email(db, payload.email)
    return {"message": "If the account exists, a password reset email will be sent"}


@router.post("/reset-password")
async def reset_password(payload: PasswordResetConfirmRequest):
    return {
        "message": "Password reset accepted",
        "status": "pending_email_provider",
        "token_preview": payload.token[:6],
    }


@router.post("/verify-email")
async def verify_email(payload: EmailVerificationRequest):
    return {
        "message": "Email verification accepted",
        "status": "pending_email_provider",
        "token_preview": payload.token[:6],
    }
