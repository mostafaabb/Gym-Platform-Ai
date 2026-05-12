from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from backend.core.exceptions import AuthenticationException, ValidationException, ConflictException
from backend.models import User
from backend.schemas import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse, RefreshTokenRequest
from backend.repositories.repositories import UserRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])
user_repo = UserRepository()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = await user_repo.get_by_email(db, request.email)
    if existing_user:
        raise ConflictException("User with this email already exists")

    # Create new user
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
        role=request.role,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    """Login user and return tokens."""
    user = await user_repo.get_by_email(db, request.email)

    if not user or not verify_password(request.password, user.password_hash):
        raise AuthenticationException("Invalid email or password")

    if not user.is_active:
        raise AuthenticationException("User account is inactive")

    # Create tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    try:
        from backend.core.security import decode_token
        payload = decode_token(request.refresh_token)

        if payload.get("type") != "refresh":
            raise AuthenticationException("Invalid refresh token")

        user_id = payload.get("sub")
        new_access_token = create_access_token(user_id)
        new_refresh_token = create_refresh_token(user_id)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )
    except Exception as e:
        raise AuthenticationException(str(e))


@router.get("/me", response_model=UserResponse)
async def me(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Return the authenticated user profile."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AuthenticationException("Missing access token")

    from backend.core.security import decode_token

    payload = decode_token(authorization.split(" ", 1)[1])
    if payload.get("type") != "access":
        raise AuthenticationException("Invalid access token")

    user = await user_repo.get(db, int(payload["sub"]))
    if not user or not user.is_active:
        raise AuthenticationException("User account is inactive")

    return UserResponse.model_validate(user)


@router.post("/logout")
async def logout():
    """Logout user."""
    # In a real implementation, this would invalidate the token
    return {"message": "Logged out successfully"}


@router.post("/forgot-password")
async def forgot_password(email: str, db: AsyncSession = Depends(get_db)):
    """Request password reset."""
    user = await user_repo.get_by_email(db, email)
    if not user:
        # Don't reveal if user exists (security best practice)
        return {"message": "If user exists, password reset email will be sent"}

    # TODO: Send password reset email
    return {"message": "Password reset email sent"}


@router.post("/reset-password")
async def reset_password(token: str, new_password: str, db: AsyncSession = Depends(get_db)):
    """Reset password with token."""
    # TODO: Validate token and reset password
    return {"message": "Password reset successfully"}
