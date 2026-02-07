import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from .base import BaseTool, ToolResult


class LinkCheckerTool(BaseTool):
    name = "Link Checker"
    description = "Scan a webpage and report broken links (404)."

    def validate(self, params: dict) -> str | None:
        url = (params.get("url") or "").strip()
        if not url:
            return "Please enter a URL."
        return None

    def _is_http_url(self, u: str) -> bool:
        try:
            p = urlparse(u)
            return p.scheme in ("http", "https")
        except Exception:
            return False

    def run(self, params: dict) -> ToolResult:
        err = self.validate(params)
        if err:
            return ToolResult(False, err)

        base_url = params["url"].strip()
        try:
            timeout = max(1, int(params.get("timeout", 10)))
        except (TypeError, ValueError):
            timeout = 10
        show_errors = bool(params.get("show_errors", False))

        try:
            page = requests.get(base_url, timeout=timeout, headers={"User-Agent": "AutomationHub/1.0"})
            if hasattr(page, "raise_for_status"):
                page.raise_for_status()
            elif getattr(page, "status_code", 200) >= 400:
                return ToolResult(False, f"Error accessing the page: HTTP {page.status_code}")
        except requests.RequestException as e:
            return ToolResult(False, f"Error accessing the page: {e}")

        soup = BeautifulSoup(page.text, "html.parser")
        anchors = soup.find_all("a")

        checked = 0
        broken_404: list[str] = []
        other_errors: list[str] = []

        for a in anchors:
            href = a.get("href")
            if not href:
                continue
            href = href.strip()

            # skip anchors and non-web schemes
            if href.startswith("#"):
                continue
            if href.startswith(("mailto:", "tel:", "javascript:", "data:")):
                continue

            full = urljoin(base_url, href)
            if not self._is_http_url(full):
                continue

            checked += 1
            try:
                r = requests.get(full, timeout=timeout, headers={"User-Agent": "AutomationHub/1.0"})
                if r.status_code == 404:
                    broken_404.append(full)
            except requests.RequestException as e:
                if show_errors:
                    other_errors.append(f"{full} ({e})")

        msg_lines = [
            f"Scanned: {base_url}",
            f"Links found: {len(anchors)} | HTTP links checked: {checked}",
            f"Broken (404): {len(broken_404)}"
        ]

        if broken_404:
            msg_lines.append("")
            msg_lines.append("404 links:")
            msg_lines.extend([f"- {u}" for u in broken_404])

        if show_errors and other_errors:
            msg_lines.append("")
            msg_lines.append("Other errors:")
            msg_lines.extend([f"- {x}" for x in other_errors])

        return ToolResult(True, "\n".join(msg_lines), {"broken_404": broken_404, "other_errors": other_errors})
