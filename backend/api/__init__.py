from fastapi import APIRouter
from backend.api import auth, gyms, workouts, analytics, ai, trainers, nutrition

# Create main router
api_router = APIRouter(prefix="/api/v1")

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(gyms.router)
api_router.include_router(workouts.router)
api_router.include_router(analytics.router)
api_router.include_router(ai.router)
api_router.include_router(trainers.router)
api_router.include_router(nutrition.router)
