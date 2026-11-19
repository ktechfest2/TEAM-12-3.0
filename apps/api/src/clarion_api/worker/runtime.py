"""Gives queued jobs the same container the API uses.

In one process (tests, single node dev) the API registers its container here.
A separate worker process builds its own the first time a job needs it.
"""

from clarion_api.api.container import Container, build_container
from clarion_api.config import get_settings

_container: Container | None = None


def use_container(container: Container | None) -> None:
    global _container  # noqa: PLW0603 - one container per process by design
    _container = container


def worker_container() -> Container:
    global _container  # noqa: PLW0603
    if _container is None:
        _container = build_container(get_settings())
    return _container
