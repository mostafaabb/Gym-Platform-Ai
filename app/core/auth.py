from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    sub: str
    exp: datetime | None = None
    type: str = "access"


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT refresh token (longer expiry)"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=30)

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        sub: str = payload.get("sub")
        token_type_check = payload.get("type", "access")

        if sub is None or token_type_check != token_type:
            return None

        return TokenData(sub=sub, type=token_type_check)
    except JWTError:
        return None


def create_email_verification_token(email: str, expires_delta: timedelta | None = None) -> str:
    """Create email verification token"""
    to_encode = {"sub": email, "type": "email_verification"}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def verify_email_token(token: str) -> Optional[str]:
    """Verify email token and return email"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        email: str = payload.get("sub")
        token_type = payload.get("type")

        if email is None or token_type != "email_verification":
            return None

        return email
    except JWTError:
        return None


def create_password_reset_token(email: str, expires_delta: timedelta | None = None) -> str:
    """Create password reset token"""
    to_encode = {"sub": email, "type": "password_reset"}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify password reset token and return email"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        email: str = payload.get("sub")
        token_type = payload.get("type")

        if email is None or token_type != "password_reset":
            return None

        return email
    except JWTError:
        return None
