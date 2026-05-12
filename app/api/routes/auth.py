from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.api.deps import get_db, get_current_user
from app.core.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_email_token,
    create_email_verification_token,
    create_password_reset_token,
    verify_password_reset_token,
    TokenResponse,
)
from db.models import User, UserRole

router = APIRouter(prefix="/auth", tags=["authentication"])


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.member


class RegisterResponse(BaseModel):
    id: int
    email: str
    full_name: str
    message: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class EmailVerificationRequest(BaseModel):
    token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db), background_tasks: BackgroundTasks = BackgroundTasks()):
    """Register new user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Create new user
    user = User(
        email=request.email,
        full_name=request.full_name,
        hashed_password=get_password_hash(request.password),
        role=request.role,
        email_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Send verification email (background task)
    verification_token = create_email_verification_token(user.email)
    background_tasks.add_task(send_verification_email, user.email, verification_token)

    return RegisterResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        message="User registered successfully. Please verify your email."
    )


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=60 * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token"""
    token_data = verify_token(request.refresh_token, token_type="refresh")

    if token_data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    user_id = int(token_data.sub)
    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    new_access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=60 * 60,
    )


@router.post("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(request: EmailVerificationRequest, db: Session = Depends(get_db)):
    """Verify user email"""
    email = verify_email_token(request.token)

    if email is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.email_verified = True
    db.commit()

    return {"message": "Email verified successfully"}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db), background_tasks: BackgroundTasks = BackgroundTasks()):
    """Request password reset"""
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    reset_token = create_password_reset_token(user.email)
    background_tasks.add_task(send_password_reset_email, user.email, reset_token)

    return {"message": "Password reset email sent"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password with token"""
    email = verify_password_reset_token(request.token)

    if email is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.hashed_password = get_password_hash(request.new_password)
    db.commit()

    return {"message": "Password reset successfully"}


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(current_user: User = Depends(get_current_user)):
    """Logout user (token invalidation handled client-side)"""
    return {"message": "Logged out successfully"}


def send_verification_email(email: str, token: str):
    """Send verification email (placeholder)"""
    pass


def send_password_reset_email(email: str, token: str):
    """Send password reset email (placeholder)"""
    pass
