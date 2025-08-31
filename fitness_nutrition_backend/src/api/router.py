from fastapi import APIRouter

from src.auth.router import router as auth_router
from src.users.router import router as users_router
from src.workouts.router import router as workouts_router
from src.diet.router import router as diet_router
from src.clients.router import router as clients_router
from src.subscriptions.router import router as subscriptions_router
from src.reports.router import router as reports_router
from src.notifications.router import router as notifications_router
from src.protocols.router import router as protocols_router
from src.settings.router import router as settings_router

api_router = APIRouter()

# Root level health check for /api
@api_router.get("/", summary="API Health", tags=["health"])
def api_health():
    return {"status": "ok"}

# Include domain routers
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(workouts_router, prefix="/workouts", tags=["workouts"])
api_router.include_router(diet_router, prefix="/diet", tags=["diet"])
api_router.include_router(clients_router, prefix="/clients", tags=["clients"])
api_router.include_router(protocols_router, prefix="/protocols", tags=["protocols"])
api_router.include_router(subscriptions_router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
api_router.include_router(settings_router, prefix="/settings", tags=["settings"])
