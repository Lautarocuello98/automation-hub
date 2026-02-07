import webbrowser

from .base import BaseTool, ToolResult


class SocialShortcutsTool(BaseTool):
    name = "Social Shortcuts"
    description = "Open a configured social/network shortcut in the browser."

    def __init__(self, socials: dict[str, str]):
        self.socials = socials

    def validate(self, params: dict) -> str | None:
        platform = params.get("platform")
        if not platform:
            return "Choose a platform."
        if platform not in self.socials:
            return f"Unknown platform: {platform}"
        return None

    def run(self, params: dict) -> ToolResult:
        err = self.validate(params)
        if err:
            return ToolResult(False, err)

        platform = params["platform"]
        url = self.socials[platform]
        webbrowser.open(url)
        return ToolResult(True, f"Opened: {platform}", {"url": url})
