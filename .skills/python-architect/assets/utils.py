"""
utils.py — Pure helper functions and generators.

Rules:
- All functions must be pure (no I/O, no side effects).
- Prefer generators over building full intermediate lists.
- Use pathlib.Path instead of os.path everywhere.
- Use re.compile() at module level — never inside loops.
"""
import re
from collections.abc import Generator
from pathlib import Path


# ---------------------------------------------------------------------------
# Domain sanitization
# ---------------------------------------------------------------------------
_WILDCARD_RE = re.compile(r"^\*\.")
_VALID_DOMAIN_RE = re.compile(
    r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?"
    r"(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*"
    r"\.[a-zA-Z]{2,}$"
)


def iter_clean(raw: list[str], root: str) -> Generator[str, None, None]:
    """
    Lazy generator that normalizes and filters raw domain strings.

    Complexity: O(n) time, O(1) extra memory (streams one item at a time).

    Args:
        raw:  Flat list of raw strings from fetchers.
        root: Root domain to filter against (e.g. "example.com").

    Yields:
        Clean, valid subdomain strings.
    """
    for entry in raw:
        if not entry or not isinstance(entry, str):
            continue
        entry = _WILDCARD_RE.sub("", entry.strip().lower())
        if not _VALID_DOMAIN_RE.match(entry):
            continue
        if entry != root and not entry.endswith(f".{root}"):
            continue
        yield entry


def sanitize(raw: list[str], root: str) -> list[str]:
    """
    Returns a sorted, deduplicated list of clean subdomains.

    Wraps iter_clean with set deduplication. Output is stable (sorted).
    """
    return sorted(set(iter_clean(raw, root)))


# ---------------------------------------------------------------------------
# Filesystem helpers (use pathlib, never os.path)
# ---------------------------------------------------------------------------

def ensure_dir(path: Path) -> Path:
    """Create directory (and parents) if it doesn't exist. Return path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json_result(path: Path, data: dict) -> None:  # type: ignore[type-arg]
    """Write a dict to a JSON file, creating parent dirs as needed."""
    import json
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Generic helpers with PEP 695 syntax
# ---------------------------------------------------------------------------

def first[T](items: list[T]) -> T | None:  # noqa: E501  (PEP 695 — Python 3.12+)
    """Return the first element of a list, or None if empty."""
    return items[0] if items else None


def chunk[T](items: list[T], size: int) -> Generator[list[T], None, None]:
    """Yield successive chunks of `size` from `items`."""
    for i in range(0, len(items), size):
        yield list(items[i : i + size])
