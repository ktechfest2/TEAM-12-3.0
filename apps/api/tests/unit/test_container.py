from clarion_api.api.container import build_container
from clarion_api.config import AppEnv, Settings
from clarion_api.repositories.memory import MemoryClaimRepository, MemorySourceRepository
from clarion_api.repositories.sql import SqlClaimRepository, SqlSourceRepository


def _settings(backend: str) -> Settings:
    return Settings(app_env=AppEnv.TEST, repository_backend=backend, _env_file=None)  # type: ignore[call-arg,arg-type]


async def test_memory_backend_is_the_default_choice() -> None:
    container = build_container(_settings("memory"))
    assert isinstance(container.sources, MemorySourceRepository)
    assert isinstance(container.claims, MemoryClaimRepository)
    assert container.engine is None
    await container.aclose()


async def test_sql_backend_builds_sql_repositories() -> None:
    container = build_container(_settings("sql"))
    assert isinstance(container.sources, SqlSourceRepository)
    assert isinstance(container.claims, SqlClaimRepository)
    assert container.engine is not None
    await container.aclose()
