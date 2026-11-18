from fastapi import APIRouter

from clarion_api.api.routes import claims, health, tools

router = APIRouter()
router.include_router(health.router)
router.include_router(claims.router)
router.include_router(tools.router)

__all__ = ["router"]
