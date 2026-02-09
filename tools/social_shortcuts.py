from __future__ import annotations

import webbrowser
from typing import Any

from .errors import ValidationError
from .types import Result


class SocialShortcutsTool:
    description = "Open a configured social/network shortcut in the browser."

    def __init__(self, socials: dict[str, str]):
        self.socials = socials

    def run(self, params: dict[str, Any]) -> Result:
        platform = str(params.get("platform", "")).strip()
        if not platform:
            raise ValidationError("Choose a platform.")
        if platform not in self.socials:
            raise ValidationError(f"Unknown platform: {platform}")

        url = self.socials[platform]
        webbrowser.open(url)
        return Result(True, f"Opened: {platform}", {"url": url})