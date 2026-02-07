import types

class DummyResp:
    def __init__(self, text="", status_code=200, content=b""):
        self.text = text
        self.status_code = status_code
        self.content = content

def test_quick_search_does_not_crash(monkeypatch):
    # Evita que abra el navegador si tu tool usa webbrowser.open
    import webbrowser
    monkeypatch.setattr(webbrowser, "open", lambda *a, **k: True)

    from tools.quick_search import QuickSearchTool

    tool = QuickSearchTool({"Google": "https://www.google.com/search?q={query}"})
    res = tool.run({"engine": "Google", "query": "hello"})
    assert hasattr(res, "ok")
    assert hasattr(res, "message")

def test_link_checker_no_internet(monkeypatch):
    # Mock requests.get para no usar internet
    import requests
    monkeypatch.setattr(
        requests,
        "get",
        lambda *a, **k: DummyResp(
            text="<html><body><a href='https://example.com/a'>a</a></body></html>",
            status_code=200,
        ),
    )

    from tools.link_checker import LinkCheckerTool

    tool = LinkCheckerTool()
    res = tool.run({"url": "https://example.com", "timeout": 5, "show_errors": False})
    assert hasattr(res, "ok")
    assert hasattr(res, "message")
