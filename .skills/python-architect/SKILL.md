---
name: python-architect
description: >
  Blueprint for designing and implementing production-ready Python modules and packages.
  Trigger: When the user asks to create a new Python module, library, installable package,
  service, or CLI tool — especially when they mention Clean Architecture, SOLID, pyproject.toml,
  async Python, modern typing, or "professional Python structure".
license: Apache-2.0
metadata:
  author: carloscapella
  version: "1.0"
  scope: [python, architecture, packaging, async, testing]
  auto_invoke:
    - "Creating a new Python package"
    - "Designing a Python library or module"
    - "Setting up pyproject.toml"
    - "Structuring a Python project"
    - "Python Clean Architecture"
    - "Production-ready Python module"
allowed-tools: Read, Edit, Write, Bash
---

## When to Use

- User asks to scaffold a **new Python package or library**.
- User needs a **Clean Architecture / SOLID** project structure in Python.
- User mentions `pyproject.toml`, `hatchling`, `poetry`, or installable package.
- User wants **async Python**, modern typing (PEP 695), or dataclasses/Pydantic models.
- User asks for a **professional Python module** ready for production or publication.

---

## Canonical Project Structure

Always deliver this layout. Do not deviate unless the user explicitly asks.

```
{project_name}/
├── pyproject.toml          ← Package metadata, deps, tooling config
├── README.md               ← Professional docs (architecture + usage)
├── .gitignore
├── .env.example            ← All env vars with safe placeholder values
├── src/
│   └── {skill_name}/
│       ├── __init__.py     ← Public API surface (only export what's needed)
│       ├── config.py       ← Env-driven config using pydantic-settings
│       ├── models.py       ← Domain models (dataclass / Pydantic BaseModel)
│       ├── service.py      ← Business logic (pure functions or async service)
│       ├── utils.py        ← Pure helpers, generators, sanitizers
│       └── exceptions.py   ← Custom typed exceptions with context
└── tests/
    ├── conftest.py         ← Shared fixtures (event_loop, mock sessions, etc.)
    └── test_service.py     ← Functional tests (at least 2 async scenarios)
```

---

## Critical Patterns

### 1. pyproject.toml — ALWAYS use, never setup.py

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{package-name}"
version = "1.0.0"
requires-python = ">=3.12"
dependencies = ["aiohttp>=3.9", "pydantic>=2.6", "python-dotenv>=1.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-asyncio>=0.23", "ruff>=0.4", "mypy>=1.10"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### 2. Config — Pydantic Settings, env-driven, singleton

```python
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    max_connections: int = 50
    global_timeout: int = 20
    log_level: str = "INFO"

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
```

### 3. Models — Pydantic BaseModel + slots dataclass

```python
# Use Pydantic for external/validated data (API input/output)
from pydantic import BaseModel, field_validator

class ReconResult(BaseModel):
    target: str
    subdomains: list[str]
    source: str

    @field_validator("target")
    @classmethod
    def target_must_be_valid(cls, v: str) -> str:
        if "." not in v:
            raise ValueError("Target must be a valid domain")
        return v.lower()

# Use @dataclass(slots=True) for internal, performance-critical DTOs
from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class FetchContext:
    target: str
    timeout: int
```

### 4. Exceptions — Typed, contextual, never naked `Exception`

```python
class ReconError(Exception):
    """Base for all recon_architect errors."""

class FetcherTimeoutError(ReconError):
    def __init__(self, fetcher: str, target: str) -> None:
        super().__init__(f"Fetcher '{fetcher}' timed out on target '{target}'")
        self.fetcher = fetcher
        self.target = target

class EmptyResponseError(ReconError):
    def __init__(self, fetcher: str) -> None:
        super().__init__(f"Fetcher '{fetcher}' returned empty response")
```

### 5. Service — async, thin, dependency-injected

```python
import asyncio
import logging

logger = logging.getLogger(__name__)

class ReconService:
    """Orchestrates all fetchers and returns sanitized results."""

    def __init__(self, fetchers: list[BaseFetcher], settings: Settings) -> None:
        self._fetchers = fetchers
        self._settings = settings

    async def run(self, target: str) -> list[str]:
        async with aiohttp.ClientSession(
            timeout=ClientTimeout(total=self._settings.global_timeout),
            connector=TCPConnector(limit=self._settings.max_connections),
        ) as session:
            tasks = [f.fetch(session, target) for f in self._fetchers]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        aggregated: list[str] = []
        for fetcher, result in zip(self._fetchers, results):
            match result:
                case Exception() as err:
                    logger.warning("Fetcher %s failed: %s", fetcher.NAME, err)
                case list() as items:
                    aggregated.extend(items)

        return sanitize(aggregated, target)
```

> **Key rule**: Use `match/case` (Python 3.10+) instead of `isinstance` chains for type dispatch.

### 6. Utils — Pure functions, generators, no side effects

```python
import re
from collections.abc import Generator

_WILDCARD_RE = re.compile(r"^\*\.")
_VALID_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61})?(\.[a-zA-Z0-9\-]+)*\.[a-zA-Z]{2,}$")

def iter_clean(raw: list[str], root: str) -> Generator[str, None, None]:
    """Lazy generator: strip, normalize, validate. O(n) time, O(1) memory."""
    for entry in raw:
        entry = _WILDCARD_RE.sub("", entry.strip().lower())
        if _VALID_RE.match(entry) and (entry == root or entry.endswith(f".{root}")):
            yield entry

def sanitize(raw: list[str], root: str) -> list[str]:
    return sorted(set(iter_clean(raw, root)))
```

> Use **generators** for sanitization — never build a full intermediate list if you can stream.

### 7. PEP 695 Type Aliases (Python 3.12+)

```python
# New syntax: type keyword (PEP 695)
type DomainList = list[str]
type FetcherResult = list[str] | Exception

# Generic type parameters (PEP 695)
def first[T](items: list[T]) -> T | None:
    return items[0] if items else None
```

### 8. Testing — pytest-asyncio, fixtures, mocks

```python
import pytest
from aioresponses import aioresponses
from recon_architect.service import ReconService
from recon_architect.config import Settings

@pytest.fixture
def settings() -> Settings:
    return Settings(max_connections=5, global_timeout=5)

@pytest.mark.asyncio
async def test_run_returns_sorted_unique_subdomains(settings):
    with aioresponses() as m:
        m.get("https://crt.sh/?q=%.example.com&output=json", payload=[
            {"name_value": "api.example.com"},
            {"name_value": "*.example.com"},   # should be sanitized
            {"name_value": "api.example.com"}, # should be deduplicated
        ])
        service = ReconService(fetchers=[CrtshFetcher()], settings=settings)
        results = await service.run("example.com")

    assert results == ["api.example.com"]

@pytest.mark.asyncio
async def test_dead_fetcher_does_not_crash_engine(settings):
    """A fetcher that always raises must NOT kill the whole run."""
    class DeadFetcher(BaseFetcher):
        NAME = "dead"
        async def fetch(self, session, target): raise RuntimeError("Network down")

    service = ReconService(fetchers=[DeadFetcher()], settings=settings)
    results = await service.run("example.com")
    assert results == []   # Graceful degradation
```

---

## Performance Decisions Table

| Concern | Solution | Location |
|:---|:---|:---|
| Concurrent fetching | `asyncio.gather + return_exceptions=True` | `service.py` |
| TCP connection pooling | `TCPConnector(limit=N)` | `service.py` |
| Deduplication | `set()` over generator | `utils.py` |
| Config overhead | `@lru_cache(maxsize=1)` on Settings factory | `config.py` |
| Memory efficiency | `Generator[str, None, None]` for sanitization | `utils.py` |
| Slot performance | `@dataclass(slots=True)` on hot DTOs | `models.py` |
| Heavy import avoidance | Lazy imports inside async functions when possible | All modules |

---

## Environment Setup Commands

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS

# Install with dev dependencies
pip install -U pip
pip install -e ".[dev]"

# Run tests
pytest -v

# Lint & type-check
ruff check src/ tests/
mypy src/
```

---

## Resources

- **Templates**: See [assets/](assets/) for ready-to-use template files: `pyproject.toml`, `.env.example`, `config.py`, `models.py`, `service.py`, `utils.py`, `exceptions.py`, `conftest.py`, `test_service.py`
- **Reference**: [PEP 695 – Type Parameter Syntax](https://peps.python.org/pep-0695/)
- **Reference**: [pydantic-settings docs](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
