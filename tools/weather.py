from __future__ import annotations

from typing import Any

import requests

from .errors import NetworkError, ValidationError
from .types import Result


class WeatherTool:
    description = "Get current weather for a city (uses wttr.in JSON, no API key)."

    def run(self, params: dict[str, Any]) -> Result:
        city = str(params.get("city", "")).strip()
        if not city:
            raise ValidationError("Please enter a city.")

        url = f"https://wttr.in/{city}?format=j1"

        try:
            r = requests.get(url, timeout=12, headers={"User-Agent": "AutomationHub/1.0"})
            r.raise_for_status()
            data = r.json()

            current = (data.get("current_condition") or [{}])[0]
            temp_c = current.get("temp_C")
            feels_c = current.get("FeelsLikeC")
            humidity = current.get("humidity")
            wind_kmph = current.get("windspeedKmph")
            desc = ((current.get("weatherDesc") or [{}])[0].get("value")) or "N/A"

            msg = (
                f"{city} | {desc}\n"
                f"Temp: {temp_c}°C (feels {feels_c}°C) | Humidity: {humidity}% | Wind: {wind_kmph} km/h"
            )
            return Result(True, msg, {"city": city, "raw": data})

        except requests.RequestException as e:
            raise NetworkError(f"Weather request failed: {e}") from e
        except ValueError as e:
            raise NetworkError("Weather response was not valid JSON.") from e
