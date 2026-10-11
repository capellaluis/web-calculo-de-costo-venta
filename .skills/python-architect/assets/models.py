"""
models.py — Domain models and data transfer objects.

Rule of thumb:
- Use Pydantic BaseModel for boundary objects (API I/O, validated input).
- Use @dataclass(slots=True, frozen=True) for internal, hot-path DTOs.
- Use PEP 695 'type' aliases for complex type expressions (Python 3.12+).
"""
from dataclasses import dataclass
from pydantic import BaseModel, field_validator

# ---------------------------------------------------------------------------
# PEP 695 Type Aliases (Python 3.12+)
# ---------------------------------------------------------------------------
type DomainName = str
type ResultList = list[str]


# ---------------------------------------------------------------------------
# Pydantic — validated boundary object
# ---------------------------------------------------------------------------
class ReconResult(BaseModel):
    """Validated output model returned to callers."""

    target: DomainName
    subdomains: ResultList
    total: int = 0

    @field_validator("target")
    @classmethod
    def normalize_target(cls, v: str) -> str:
        v = v.strip().lower()
        if "." not in v:
            raise ValueError(f"'{v}' is not a valid domain name")
        return v

    def model_post_init(self, __context: object) -> None:  # noqa: ANN001
        # Auto-compute total after validation
        object.__setattr__(self, "total", len(self.subdomains))


# ---------------------------------------------------------------------------
# Dataclass — internal, memory-efficient DTO
# ---------------------------------------------------------------------------
@dataclass(slots=True, frozen=True)
class FetchContext:
    """Immutable context passed from engine to each fetcher."""

    target: DomainName
    timeout: int
    source_name: str
