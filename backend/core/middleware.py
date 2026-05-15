from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.config import get_settings
from backend.core.database import async_session_maker
from backend.core.security import decode_token
from backend.models import AuditLog

settings = get_settings()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(self), microphone=(self)"
        response.headers["X-XSS-Protection"] = "0"
        if settings.ENVIRONMENT != "development":
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Small in-process limiter for local/dev; swap with Redis in clustered production."""

    def __init__(self, app):
        super().__init__(app)
        self._buckets: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if not settings.RATE_LIMIT_ENABLED or request.url.path in {"/health", "/docs", "/openapi.json"}:
            return await call_next(request)

        key = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
        bucket = self._buckets[key]
        now = time.time()
        window_start = now - settings.RATE_LIMIT_PERIOD

        while bucket and bucket[0] < window_start:
            bucket.popleft()

        if len(bucket) >= settings.RATE_LIMIT_REQUESTS:
            return Response(
                content='{"error_code":"RATE_LIMIT_EXCEEDED","message":"Too many requests"}',
                media_type="application/json",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        bucket.append(now)
        return await call_next(request)


from fastapi import Request, Response, status, BackgroundTasks

# ... existing imports ...

class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)

        should_log = request.url.path.startswith(settings.API_V1_STR) and request.method in {
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        }
        if not should_log:
            return response

        user_id: int | None = None
        authorization = request.headers.get("authorization")
        if authorization and authorization.lower().startswith("bearer "):
            try:
                token = authorization.split(" ", 1)[1]
                # We use the existing decode_token but we don't want it to raise
                # errors here if the token is just expired or invalid
                from jose import jwt
                payload = jwt.get_unverified_claims(token)
                if payload and "sub" in payload:
                    user_id = int(payload["sub"])
            except Exception:
                user_id = None

        # Prepare log data
        log_data = {
            "user_id": user_id,
            "action": f"{request.method} {request.url.path}",
            "resource_type": request.url.path.split("/")[-2] if "/" in request.url.path else "api",
            "ip_address": request.headers.get("x-forwarded-for")
            or (request.client.host if request.client else None),
            "user_agent": request.headers.get("user-agent"),
            "status_code": response.status_code,
        }

        # Define the background logging task
        async def log_to_db(data: dict):
            try:
                async with async_session_maker() as session:
                    session.add(
                        AuditLog(
                            user_id=data["user_id"],
                            action=data["action"],
                            resource_type=data["resource_type"],
                            resource_id=None,
                            ip_address=data["ip_address"],
                            user_agent=data["user_agent"],
                            new_values={"status_code": data["status_code"]},
                        )
                    )
                    await session.commit()
            except Exception as e:
                # Log the error but don't crash the request
                import logging
                logging.getLogger(__name__).error(f"Failed to write audit log: {e}")

        # In Starlette BaseHTTPMiddleware, we can't easily add to BackgroundTasks 
        # of the response because the response is already created. 
        # However, we can just fire and forget or use a separate task runner.
        import asyncio
        asyncio.create_task(log_to_db(log_data))

        return response
