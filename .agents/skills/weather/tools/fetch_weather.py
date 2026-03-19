#!/usr/bin/env python3
"""Fetch weather data from OpenWeatherMap API.

Usage:
    python fetch_weather.py [options]

Options:
    --location LOC     Location: city name, ZIP code, or "lat,lon"
    --appid APIKEY     OpenWeatherMap API key (can also use WEATHER_API_KEY env var)
    --mode MODE        weather (current), forecast (5-day), or both (default: weather)
    --units UNITS      metric or imperial (default: metric)
    --output FILE      Write output to FILE instead of stdout
    --format           text or json (default: text)

Examples:
    python fetch_weather.py --location "San Francisco, CA"
    python fetch_weather.py --location "90210" --mode forecast
    python fetch_weather.py --location "lat:40.7128,lon:-74.0060" --units imperial
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime


def parse_location(loc: str) -> str:
    """Parse location string into API query parameter."""
    if loc.startswith("lat:"):
        parts = loc.replace("lon:", ",").replace("lat:", "").split(",")
        if len(parts) == 2:
            return f"{parts[0].strip()},{parts[1].strip()}"
    return loc


def fetch_weather(location: str, api_key: str, units: str = "metric") -> dict:
    """Fetch current weather data."""
    query = parse_location(location)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={query}&appid={api_key}&units={units}"
    return _fetch_json(url)


def fetch_forecast(location: str, api_key: str, units: str = "metric") -> dict:
    """Fetch 5-day forecast data."""
    query = parse_location(location)
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={query}&appid={api_key}&units={units}"
    return _fetch_json(url)


def _fetch_json(url: str) -> dict:
    """Fetch and parse JSON from URL."""
    req = urllib.request.Request(url, headers={"User-Agent": "weather-tool/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def format_current(data: dict, units: str) -> str:
    """Format current weather data as text."""
    if "cod" in data and data["cod"] != 200:
        return f"Error: {data.get('message', 'Unknown error')}"

    weather = data["weather"][0]
    main = data["main"]
    wind = data.get("wind", {})

    temp_unit = "°C" if units == "metric" else "°F"
    speed_unit = "km/h" if units == "metric" else "mph"

    # Convert wind speed if needed
    wind_speed = wind.get("speed", 0)
    if units == "imperial":
        wind_speed = wind_speed  # already in mph
    else:
        wind_speed = wind_speed * 3.6  # m/s to km/h

    # Get wind direction
    wind_dir = wind.get("deg", 0)
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    wind_rose = directions[int((wind_dir + 22.5) / 45) % 8]

    # Weather emoji mapping
    emoji_map = {
        "Clear": "☀️",
        "Clouds": "☁️",
        "Rain": "🌧️",
        "Drizzle": "🌦️",
        "Thunderstorm": "⛈️",
        "Snow": "❄️",
        "Mist": "🌫️",
        "Fog": "🌫️",
        "Haze": "🌫️",
    }
    emoji = emoji_map.get(weather["main"], "🌤️")

    lines = [
        f"Current weather in {data['name']}:",
        f"{emoji} {weather['description'].capitalize()}",
        f"Temperature: {main['temp']}{temp_unit} (feels like {main['feels_like']}{temp_unit})",
        f"Humidity: {main['humidity']}%",
        f"Wind: {wind_speed:.1f} {speed_unit} from the {wind_rose}",
    ]
    return "\n".join(lines)


def format_forecast(data: dict, units: str) -> str:
    """Format forecast data as text."""
    if "cod" in data and data["cod"] != "200":
        return f"Error: {data.get('message', 'Unknown error')}"

    city = data["city"]["name"]
    temp_unit = "°C" if units == "metric" else "°F"

    # Group forecasts by day
    daily = {}
    for item in data["list"]:
        date = item["dt_txt"].split()[0]
        if date not in daily:
            daily[date] = []
        daily[date].append(item)

    lines = [f"5-day forecast for {city}:", ""]

    # Weather emoji mapping
    emoji_map = {
        "Clear": "☀️",
        "Clouds": "☁️",
        "Rain": "🌧️",
        "Drizzle": "🌦️",
        "Thunderstorm": "⛈️",
        "Snow": "❄️",
        "Mist": "🌫️",
        "Fog": "🌫️",
    }

    for date, forecasts in sorted(daily.items())[:5]:
        # Get noon forecast for the day
        noon_forecasts = [f for f in forecasts if "12:00:00" in f["dt_txt"]]
        if noon_forecasts:
            f = noon_forecasts[0]
        else:
            f = forecasts[0]

        weather = f["weather"][0]
        main = f["main"]
        emoji = emoji_map.get(weather["main"], "🌤️")

        # Calculate min/max from all forecasts for the day
        temps = [item["main"]["temp"] for item in forecasts]
        temp_min = min(temps)
        temp_max = max(temps)

        date_obj = datetime.strptime(date, "%Y-%m-%d")
        date_str = date_obj.strftime("%a, %b %d")

        lines.append(f"{date_str}: {emoji} {weather['description'].capitalize()}")
        lines.append(
            f"       {temp_min:.0f}-{temp_max:.0f}{temp_unit}, Humidity: {main['humidity']}%"
        )

    return "\n".join(lines)


def format_both(current: dict, forecast: dict, units: str) -> str:
    """Format both current and forecast data."""
    return format_current(current, units) + "\n\n" + format_forecast(forecast, units)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch weather data from OpenWeatherMap."
    )
    parser.add_argument(
        "--location", required=True, help="Location (city, ZIP, or lat,lon)"
    )
    parser.add_argument("--appid", default=None, help="OpenWeatherMap API key")
    parser.add_argument(
        "--mode", choices=["weather", "forecast", "both"], default="weather"
    )
    parser.add_argument("--units", choices=["metric", "imperial"], default="metric")
    parser.add_argument("--output", default=None, help="Output file")
    parser.add_argument(
        "--format", choices=["text", "json"], default="json", dest="fmt"
    )
    args = parser.parse_args()

    # Get API key
    api_key = args.appid or os.environ.get("WEATHER_API_KEY")
    if not api_key:
        sys.exit("Error: WEATHER_API_KEY environment variable or --appid required.")

    try:
        result = {}
        if args.mode in ["weather", "both"]:
            result["current"] = fetch_weather(args.location, api_key, args.units)
        if args.mode in ["forecast", "both"]:
            result["forecast"] = fetch_forecast(args.location, api_key, args.units)
    except urllib.error.HTTPError as e:
        sys.exit(f"API Error: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        sys.exit(f"Network Error: {e.reason}")

    if args.fmt == "json":
        output = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        if args.mode == "both":
            output = format_both(result["current"], result["forecast"], args.units)
        elif args.mode == "forecast":
            output = format_forecast(result["forecast"], args.units)
        else:
            output = format_current(result["current"], args.units)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Saved weather data to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
