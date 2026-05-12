from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging
from backend.core.config import get_settings
from backend.core.database import init_db, close_db
from backend.core.exceptions import AppException
from backend.api import api_router

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("🚀 Starting GymFlow AI Backend...")
    await init_db()
    logger.info("✅ Database initialized")

    yield

    # Shutdown
    logger.info("🛑 Shutting down GymFlow AI Backend...")
    await close_db()
    logger.info("✅ Database closed")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Production-grade AI-powered gym operating system",
        lifespan=lifespan,
    )

    # ============== MIDDLEWARE ==============

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trusted Host
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.gymflowai.com", "*"]
        if settings.ENVIRONMENT == "development"
        else ["localhost", "127.0.0.1", "*.gymflowai.com"],
    )

    # GZIP compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ============== EXCEPTION HANDLERS ==============

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
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            },
        )

    # ============== ROUTES ==============

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }

    @app.get("/api/v1/docs", tags=["Documentation"])
    async def api_docs():
        """API documentation."""
        return {
            "message": "API documentation available at /docs",
            "openapi_url": "/openapi.json",
        }

    app.include_router(api_router)

    return app


# Create app instance
app = create_app()
