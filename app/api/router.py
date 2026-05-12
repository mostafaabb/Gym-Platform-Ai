from fastapi import APIRouter

from app.api.routes.ai import router as ai_router
from app.api.routes.auth import router as auth_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.history import router as history_router
from app.api.routes.workouts import router as workouts_router
from app.api.routes.users import router as users_router
from app.api.routes.gyms import router as gyms_router
from app.api.routes.trainers import router as trainers_router
from app.api.routes.classes import router as classes_router
from app.api.routes.subscriptions import router as subscriptions_router
from app.api.routes.nutrition import router as nutrition_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.notifications import router as notifications_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(workouts_router)
api_router.include_router(gyms_router)
api_router.include_router(trainers_router)
api_router.include_router(classes_router)
api_router.include_router(subscriptions_router)
api_router.include_router(nutrition_router)
api_router.include_router(analytics_router)
api_router.include_router(notifications_router)
api_router.include_router(ai_router)
api_router.include_router(history_router)
api_router.include_router(dashboard_router)

