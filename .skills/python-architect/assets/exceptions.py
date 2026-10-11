"""
exceptions.py — Typed domain exceptions.

Rules:
- Every public exception MUST extend the base SkillError.
- Include context in __init__ so callers can inspect fields, not just messages.
- Never raise naked Exception or RuntimeError from library code.
"""


class SkillError(Exception):
    """Base class for all package-level errors."""


class ConfigurationError(SkillError):
    """Raised when required configuration is missing or invalid."""

    def __init__(self, key: str, reason: str) -> None:
        super().__init__(f"Configuration error for '{key}': {reason}")
        self.key = key
        self.reason = reason


class FetcherTimeoutError(SkillError):
    """Raised when a fetcher exceeds its timeout budget."""

    def __init__(self, fetcher: str, target: str) -> None:
        super().__init__(f"Fetcher '{fetcher}' timed out on target '{target}'")
        self.fetcher = fetcher
        self.target = target


class EmptyResponseError(SkillError):
    """Raised when a fetcher receives a 200 OK but with empty/null payload."""

    def __init__(self, fetcher: str) -> None:
        super().__init__(f"Fetcher '{fetcher}' returned an empty response")
        self.fetcher = fetcher


class InvalidTargetError(SkillError):
    """Raised when the target domain fails validation."""

    def __init__(self, target: str) -> None:
        super().__init__(f"'{target}' is not a valid target domain")
        self.target = target
