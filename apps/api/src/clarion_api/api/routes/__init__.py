from fastapi import APIRouter

from clarion_api.api.routes import (
    auth,
    claims,
    health,
    messages,
    public,
    subscriptions,
    tools,
    webhooks,
)

router = APIRouter()
router.include_router(health.router)
router.include_router(auth.router)
router.include_router(claims.router)
router.include_router(messages.router)
router.include_router(public.router)
router.include_router(subscriptions.router)
router.include_router(tools.router)
router.include_router(webhooks.router)

__all__ = ["router"]
