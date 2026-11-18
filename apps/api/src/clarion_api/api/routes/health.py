from fastapi import APIRouter

from clarion_api import __version__
from clarion_api.api.deps import ContainerDep
from clarion_api.api.schemas import HealthOut

router = APIRouter(tags=["health"])


@router.get("/health", operation_id="getHealth")
async def health(container: ContainerDep) -> HealthOut:
    return HealthOut(status="ok", version=__version__, env=container.settings.app_env.value)
