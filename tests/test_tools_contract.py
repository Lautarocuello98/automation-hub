from __future__ import annotations

from pathlib import Path

import pytest

from tools.errors import ValidationError
from tools.link_checker import LinkCheckerTool
from tools.quick_search import QuickSearchTool
from tools.social_shortcuts import SocialShortcutsTool
from tools.weather import WeatherTool
from tools.web_downloader import WebDownloaderTool


class DummyResp:
    def __init__(self, text="", status_code=200, content=b"", headers=None, json_data=None):
        self.text = text
        self.status_code = status_code
        self.content = content
        self.headers = headers or {}
        self._json_data = json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

    def json(self):
        if self._json_data is None:
            raise ValueError("invalid json")
        return self._json_data



def test_quick_search_returns_result(monkeypatch):
    import webbrowser

    opened: list[str] = []
    monkeypatch.setattr(webbrowser, "open", lambda url: opened.append(url) or True)

    tool = QuickSearchTool({"Google": "https://www.google.com/search?q={query}"})
    res = tool.run({"engine": "Google", "query": "hello world"})

    assert res.ok is True
    assert "Opened search" in res.message
    assert opened and "hello+world" in opened[0]


def test_social_shortcuts_validation_error():
    tool = SocialShortcutsTool({"GitHub": "https://github.com"})
    with pytest.raises(ValidationError):
        tool.run({"platform": ""})


def test_weather_returns_result_with_mock(monkeypatch):
    import requests
    
    def fake_get(*_a, **_k):
        return DummyResp(
            status_code=200,
            json_data={
                "current_condition": [
                    {
                        "temp_C": "18",
                        "FeelsLikeC": "17",
                        "humidity": "70",
                        "windspeedKmph": "12",
                        "weatherDesc": [{"value": "Cloudy"}],
                    }
                ]
            },
        )

    monkeypatch.setattr(requests, "get", fake_get)

    tool = WeatherTool()
    res = tool.run({"city": "Buenos Aires"})

    assert res.ok is True
    assert "Buenos Aires" in res.message
    assert res.data and res.data["city"] == "Buenos Aires"


def test_web_downloader_links_mode(monkeypatch, tmp_path: Path):
    import requests

    html = """
    <html><body>
      <a href="/a">A</a>
      <a href="https://example.com/b">B</a>
      <a href="#frag">F</a>
    </body></html>
    """

    monkeypatch.setattr(requests, "get", lambda *a, **k: DummyResp(text=html, status_code=200))

    tool = WebDownloaderTool()
    res = tool.run({"url": "https://example.com", "mode": "links", "out_dir": str(tmp_path)})

    assert res.ok is True
    assert res.data and res.data["links"]

    links_file = Path(res.data["links"])
    content = links_file.read_text(encoding="utf-8")
    assert "https://example.com/a" in content
    assert "https://example.com/b" in content


def test_link_checker_reports_404(monkeypatch):
    import requests

    def fake_get(url, *args, **kwargs):
        if url == "https://example.com":
            return DummyResp(text="<a href='/ok'>ok</a><a href='/missing'>missing</a>", status_code=200)
        if url.endswith("/missing"):
            return DummyResp(status_code=404)
        return DummyResp(status_code=200)

    monkeypatch.setattr(requests, "get", fake_get)

    tool = LinkCheckerTool()
    res = tool.run({"url": "https://example.com", "timeout": 5, "show_errors": False})

    assert res.ok is True
    assert res.data is not None
    assert "https://example.com/missing" in res.data["broken_404"]