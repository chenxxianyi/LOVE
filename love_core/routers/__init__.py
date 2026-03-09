from fastapi import APIRouter

from love_core.routers.auth import router as auth_router
from love_core.routers.backup import router as backup_router
from love_core.routers.couple import router as couple_router
from love_core.routers.notifications import router as notifications_router
from love_core.routers.reminders import router as reminders_router
from love_core.routers.security import router as security_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(couple_router)
router.include_router(reminders_router)
router.include_router(notifications_router)
router.include_router(security_router)
router.include_router(backup_router)
