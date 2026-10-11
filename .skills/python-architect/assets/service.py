"""
service.py — Core business logic service.

Responsibilities:
- Orchestrate async fetch tasks concurrently.
- Apply pattern matching for result dispatch.
- Delegate sanitization to utils.
- Never own HTTP sessions directly — accept them via constructor or context.

Dependency injection: Settings and fetchers are passed in (testable, SOLID).
"""
from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import aiohttp
from aiohttp import ClientTimeout, TCPConnector

from .config import Settings
from .models import ReconResult
from .utils import sanitize

if TYPE_CHECKING:
    from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)


class ReconService:
    """
    Orchestrates all registered BaseFetcher instances concurrently.

    Uses asyncio.gather with return_exceptions=True so one dead fetcher
    never blocks the rest. Results are dispatched via match/case.

    Args:
        fetchers:  List of BaseFetcher implementations to run.
        settings:  Application settings (injected for testability).
    """

    def __init__(self, fetchers: list[BaseFetcher], settings: Settings) -> None:
        self._fetchers = fetchers
        self._settings = settings

    async def run(self, target: str) -> ReconResult:
        """
        Execute all fetchers concurrently and return a validated ReconResult.

        Args:
            target: Root domain to enumerate (e.g. "example.com").

        Returns:
            ReconResult with deduplicated, sorted subdomains.
        """
        logger.info("Starting recon for target=%s with %d fetchers", target, len(self._fetchers))

        timeout = ClientTimeout(total=self._settings.global_timeout)
        connector = TCPConnector(limit=self._settings.max_connections, ssl=False)

        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            tasks = [fetcher.fetch(session, target) for fetcher in self._fetchers]
            raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        aggregated: list[str] = []

        for fetcher, result in zip(self._fetchers, raw_results, strict=True):
            match result:
                case Exception() as err:
                    logger.warning("Fetcher %r failed: %s", fetcher.NAME, err)
                case [*items]:
                    aggregated.extend(str(i) for i in items)
                case _:
                    logger.debug("Fetcher %r returned unexpected type: %s", fetcher.NAME, type(result))

        subdomains = sanitize(aggregated, target)
        logger.info("Recon complete: %d unique subdomains found for %s", len(subdomains), target)

        return ReconResult(target=target, subdomains=subdomains)
