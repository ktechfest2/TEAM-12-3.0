from clarion_api.repositories.memory import MemoryClaimRepository, MemorySourceRepository
from tests.support import repository_contract as contract


async def test_memory_source_add_and_get() -> None:
    await contract.check_source_add_and_get(MemorySourceRepository())


async def test_memory_source_get_missing_returns_none() -> None:
    await contract.check_source_get_missing(MemorySourceRepository())


async def test_memory_source_search_orders_by_similarity() -> None:
    await contract.check_source_search_orders_by_similarity(MemorySourceRepository())


async def test_memory_source_search_respects_limit() -> None:
    await contract.check_source_search_respects_limit(MemorySourceRepository())


async def test_memory_claims_add_get_and_list() -> None:
    await contract.check_claim_add_get_and_list(MemoryClaimRepository())
