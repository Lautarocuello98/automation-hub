from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .errors import NetworkError, ValidationError
from .types import Result


class WebDownloaderTool:
    description = "Download a page HTML, extract links, and/or download images."

    def _safe_name(self, text: str) -> str:
        text = text.strip().lower()
        text = re.sub(r"[^a-z0-9_\-\.]+", "_", text)
        return text[:120] or "page"

    def _is_http_url(self, u: str) -> bool:
        try:
            p = urlparse(u)
            return p.scheme in ("http", "https")
        except Exception:
            return False

    def _guess_ext(self, content_type: str) -> str:
        ct = (content_type or "").lower()
        if "jpeg" in ct or "jpg" in ct:
            return ".jpg"
        if "png" in ct:
            return ".png"
        if "webp" in ct:
            return ".webp"
        if "gif" in ct:
            return ".gif"
        return ""

    def run(self, params: dict[str, Any]) -> Result:
        url = str(params.get("url", "")).strip()
        if not url:
            raise ValidationError("Please enter a URL.")

        mode = str(params.get("mode", "all"))
        if mode not in ("html", "links", "images", "all"):
            raise ValidationError("Mode must be one of: html, links, images, all.")


        out_dir = Path(params.get("out_dir") or "downloads")
        try:
            timeout = max(1, int(params.get("timeout", 12)))
        except (TypeError, ValueError):
            timeout = 12

        out_dir.mkdir(parents=True, exist_ok=True)

        try:
            r = requests.get(url, timeout=timeout, headers={"User-Agent": "AutomationHub/1.0"})
            r.raise_for_status()
        except requests.RequestException as e:
            raise NetworkError(f"Request failed: {e}") from e

        html = r.text
        soup = BeautifulSoup(html, "html.parser")

        parsed = urlparse(url)
        page_key = self._safe_name(parsed.netloc + parsed.path)
        page_folder = out_dir / page_key
        page_folder.mkdir(parents=True, exist_ok=True)

        saved = {"html": None, "links": None, "images": 0}
        notes: list[str] = []

        if mode in ("html", "all"):
            html_path = page_folder / "page.html"
            html_path.write_text(html, encoding="utf-8", errors="ignore")
            saved["html"] = str(html_path)
            notes.append(f"Saved HTML: {html_path}")

        if mode in ("links", "all"):
            links = []
            for a in soup.find_all("a"):
                href = a.get("href")
                if not href:
                    continue
                href = href.strip()
                if href.startswith("#"):
                    continue
                if href.startswith(("mailto:", "tel:", "javascript:", "data:")):
                    continue
                full = urljoin(url, href)
                if self._is_http_url(full):
                    links.append(full)

            seen = set()
            unique_links = []
            for x in links:
                if x not in seen:
                    seen.add(x)
                    unique_links.append(x)

            links_path = page_folder / "links.txt"
            links_path.write_text("\n".join(unique_links) + "\n", encoding="utf-8")
            saved["links"] = str(links_path)
            notes.append(f"Saved links: {links_path} ({len(unique_links)} links)")

        if mode in ("images", "all"):
            images_folder = page_folder / "images"
            images_folder.mkdir(parents=True, exist_ok=True)

            img_urls = []
            for img in soup.find_all("img"):
                src = img.get("src")
                if not src:
                    continue
                src = src.strip()
                if src.startswith("data:"):
                    continue
                full = urljoin(url, src)
                if self._is_http_url(full):
                    img_urls.append(full)

            img_urls = list(dict.fromkeys(img_urls))

            count = 0
            for i, img_url in enumerate(img_urls, start=1):
                try:
                    img_r = requests.get(img_url, timeout=timeout, headers={"User-Agent": "AutomationHub/1.0"})
                    img_r.raise_for_status()

                    ext = os.path.splitext(urlparse(img_url).path)[1]
                    if not ext:
                        ext = self._guess_ext(img_r.headers.get("Content-Type", "")) or ".bin"

                    file_name = f"img_{i:03d}{ext}"
                    (images_folder / file_name).write_bytes(img_r.content)
                    count += 1
                except requests.RequestException:
                    continue

            saved["images"] = count
            notes.append(f"Downloaded images: {count} file(s) into {images_folder}")

        msg = "\n".join(
            ["Web download complete.", f"Base URL: {url}", f"Output: {page_folder}", ""] + notes
        )
        return Result(True, msg, saved)
