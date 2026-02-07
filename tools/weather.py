import requests

from .base import BaseTool, ToolResult


class WeatherTool(BaseTool):
    name = "Weather"
    description = "Get current weather for a city (uses wttr.in JSON, no API key)."

    def validate(self, params: dict) -> str | None:
        city = (params.get("city") or "").strip()
        if not city:
            return "Please enter a city."
        return None

    def run(self, params: dict) -> ToolResult:
        err = self.validate(params)
        if err:
            return ToolResult(False, err)

        city = params["city"].strip()
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
            return ToolResult(True, msg, {"city": city, "raw": data})

        except requests.RequestException as e:
            return ToolResult(False, f"Weather request failed: {e}")
        except ValueError:
            return ToolResult(False, "Weather response was not valid JSON.")
