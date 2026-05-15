from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from backend.api import api_router
from backend.core.config import get_settings
from backend.core.database import close_db, init_db
from backend.core.exceptions import AppException
from backend.core.middleware import AuditLogMiddleware, RateLimitMiddleware, SecurityHeadersMiddleware

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting GymFlow AI Backend")
    await init_db()
    logger.info("Database initialized")

    yield

    logger.info("Shutting down GymFlow AI Backend")
    await close_db()
    logger.info("Database closed")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Production-grade AI-powered gym operating system with voice coaching, "
            "pose detection, workout intelligence, analytics, and multi-tenant gym SaaS."
        ),
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(AuditLogMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.gymflowai.com", "*.onrender.com", "*"]
        if settings.ENVIRONMENT == "development"
        else ["localhost", "127.0.0.1", "*.gymflowai.com", "*.onrender.com"],
    )
    # Handle CORS origins - if "*" is in origins and credentials are required, 
    # we must use a regex or specific origins.
    cors_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS if str(origin) != "*"]
    cors_allow_all = "*" in [str(o) for o in settings.BACKEND_CORS_ORIGINS]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_origin_regex=".*" if cors_allow_all else None,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            },
        )

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "features": {
                "ai": settings.ENABLE_AI_FEATURES,
                "pose_detection": settings.ENABLE_POSE_DETECTION,
                "websockets": settings.ENABLE_WEBSOCKETS,
            },
        }

    @app.get("/api/v1/docs", tags=["Documentation"])
    async def api_docs():
        return {
            "message": "API documentation available at /docs",
            "openapi_url": f"{settings.API_V1_STR}/openapi.json",
        }

    from backend.api import websockets
    app.include_router(api_router)
    app.include_router(websockets.router)
    return app


app = create_app()
