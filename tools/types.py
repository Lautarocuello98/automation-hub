from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class Result:
    ok: bool
    message: str
    data: dict[str, Any] | None = None


class Tool(Protocol):
    """Contract for all tools used by the UI."""
    description: str

    def run(self, params: dict[str, Any]) -> Result: ...
