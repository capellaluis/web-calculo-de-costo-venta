"""
conftest.py — Shared pytest fixtures.

Loaded automatically by pytest before any test module.
Keep fixtures focused: one responsibility per fixture.
"""
import pytest
from recon_architect.config import Settings


@pytest.fixture
def settings() -> Settings:
    """Return a Settings instance with safe test-only overrides."""
    return Settings(
        max_connections=5,
        global_timeout=5,
        log_level="DEBUG",
    )
