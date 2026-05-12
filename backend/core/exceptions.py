from fastapi import HTTPException, status


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = 400, error_code: str = "ERROR"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class AuthenticationException(AppException):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, "AUTH_FAILED")


class AuthorizationException(AppException):
    """Authorization failed - user lacks permissions."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status.HTTP_403_FORBIDDEN, "FORBIDDEN")


class ResourceNotFoundException(AppException):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND, "NOT_FOUND")


class ValidationException(AppException):
    """Validation error."""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, "VALIDATION_ERROR")


class ConflictException(AppException):
    """Resource conflict."""

    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status.HTTP_409_CONFLICT, "CONFLICT")


class RateLimitException(AppException):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS, "RATE_LIMIT_EXCEEDED")
