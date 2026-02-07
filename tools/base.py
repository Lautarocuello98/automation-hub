from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ToolResult:
    ok: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class BaseTool:
    name: str = "Unnamed Tool"
    description: str = ""

    def validate(self, params: Dict[str, Any]) -> Optional[str]:
        return None

    def run(self, params: Dict[str, Any]) -> ToolResult:
        raise NotImplementedError("Tools must implement run()")
