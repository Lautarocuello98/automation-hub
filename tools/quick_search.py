import webbrowser
from urllib.parse import quote_plus

from .base import BaseTool, ToolResult


class QuickSearchTool(BaseTool):
    name = "Quick Search"
    description = "Open a search query in the browser using a selected engine."

    def __init__(self, search_engines: dict[str, str]):
        self.search_engines = search_engines

    def validate(self, params: dict) -> str | None:
        query = (params.get("query") or "").strip()
        if not query:
            return "Please enter a search query."

        engine = params.get("engine", "Google")
        if engine not in self.search_engines:
            return f"Unknown engine: {engine}"
        return None

    def run(self, params: dict) -> ToolResult:
        err = self.validate(params)
        if err:
            return ToolResult(False, err)

        engine = params.get("engine", "Google")
        query = params.get("query").strip()
        url = self.search_engines[engine].format(query=quote_plus(query))

        webbrowser.open(url)
        return ToolResult(True, f"Opened {engine} search for: {query}", {"url": url})
