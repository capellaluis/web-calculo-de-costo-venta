"""
test_service.py — Functional tests for ReconService.

Rules:
- Every test describes a behaviour, not an implementation detail.
- Use aioresponses to mock HTTP — never hit real APIs in tests.
- At minimum: one happy path + one resilience/failure path.
"""
import pytest
from aioresponses import aioresponses

from recon_architect.config import Settings
from recon_architect.base_fetcher import BaseFetcher
from recon_architect.fetchers.crtsh import CrtshFetcher
from recon_architect.service import ReconService


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_run_returns_sorted_unique_subdomains(settings: Settings) -> None:
    """Verify that results are deduplicated, sanitized, and sorted."""
    with aioresponses() as m:
        m.get(
            "https://crt.sh/?q=%.example.com&output=json",
            payload=[
                {"name_value": "api.example.com"},
                {"name_value": "*.example.com"},    # wildcard → sanitized away
                {"name_value": "api.example.com"},  # duplicate → deduplicated
                {"name_value": "mail.example.com"},
            ],
        )
        service = ReconService(fetchers=[CrtshFetcher()], settings=settings)
        result = await service.run("example.com")

    assert result.target == "example.com"
    assert result.subdomains == ["api.example.com", "mail.example.com"]
    assert result.total == 2


# ---------------------------------------------------------------------------
# Resilience path
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_dead_fetcher_does_not_crash_engine(settings: Settings) -> None:
    """A fetcher that always raises must NOT propagate — graceful degradation."""

    class DeadFetcher(BaseFetcher):
        NAME = "dead"

        async def fetch(self, session, target):  # type: ignore[override]
            raise RuntimeError("Simulated network failure")

    service = ReconService(fetchers=[DeadFetcher()], settings=settings)
    result = await service.run("example.com")

    assert result.subdomains == []
    assert result.total == 0
