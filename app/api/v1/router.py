from fastapi import APIRouter
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.profile import router as profile_router
from app.api.v1.routes.lands import router as lands_router
from app.api.v1.routes.sensors import router as sensors_router
from app.api.v1.routes.cultivation import items_router, records_router, opex_router
from app.api.v1.routes.users import router as users_router
from app.api.v1.routes.subscriptions import router as subscriptions_router
from app.api.v1.routes.admin import router as admin_router
from app.api.v1.routes.upload import router as upload_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(profile_router)
api_router.include_router(lands_router)
api_router.include_router(sensors_router)
api_router.include_router(items_router)
api_router.include_router(records_router)
api_router.include_router(opex_router)
api_router.include_router(users_router)
api_router.include_router(subscriptions_router)
api_router.include_router(admin_router)
api_router.include_router(upload_router)