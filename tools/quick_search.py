from __future__ import annotations

import webbrowser
from typing import Any
from urllib.parse import quote_plus

from .types import Result
from .errors import ValidationError


class QuickSearchTool:
    description = "Open a web search in your browser using configured engines."

    def __init__(self, engines: dict[str, str]):
        self.engines = engines

    def run(self, params: dict[str, Any]) -> Result:
        engine = str(params.get("engine", "")).strip()
        query = str(params.get("query", "")).strip()

        if not query:
            raise ValidationError("Query is empty.")

        base = self.engines.get(engine) or self.engines.get("Google")
        if not base:
            # fallback hardcoded
            base = "https://www.google.com/search?q={query}"

        url = base.format(query=quote_plus(query))
        webbrowser.open(url)
        return Result(True, f"Opened search on {engine}: {query}", {"url": url})
