#!/usr/bin/env python3
import json
import sys
import os
from urllib.parse import urlencode
from typing import Dict, List, Optional, Tuple

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
PREFERENCES_FILE = os.path.join(SKILL_DIR, "weather_preferences.json")


def load_preferences() -> Dict:
    if os.path.exists(PREFERENCES_FILE):
        try:
            with open(PREFERENCES_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_preferences(preferences: Dict):
    with open(PREFERENCES_FILE, "w") as f:
        json.dump(preferences, f, indent=2)


def validate_zipcode(zipcode: str) -> Tuple[bool, Optional[int], Optional[str]]:
    if not zipcode.isdigit():
        return False, None, "Please enter a valid 5-digit US zipcode"
    if len(zipcode) != 5:
        return False, None, "Please enter a valid 5-digit US zipcode"
    return True, int(zipcode), None


def convert_zipcode_to_coordinates(
    zipcode: int,
) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    url = f"https://nominatim.openstreetmap.org/search?postalcode={zipcode}&format=json&country=US"

    try:
        import urllib.request
        import json

        req = urllib.request.Request(url)
        req.add_header("User-Agent", "WeatherAssistant/1.0")
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

        if not data:
            return None, None, f"Could not find location for zipcode {zipcode}"

        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return lat, lon, None

    except Exception as e:
        return None, None, "Unable to look up location. Please try again."


def fetch_weather(lat: float, lon: float) -> Tuple[Optional[Dict], Optional[str]]:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=precipitation_probability,precipitation,windspeed_10m"

    try:
        import urllib.request
        import json

        req = urllib.request.Request(url)
        req.add_header("User-Agent", "WeatherAssistant/1.0")
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

        current = data["current_weather"]
        hourly = data["hourly"]

        temp_c = current["temperature"]
        temp_f = (temp_c * 9 / 5) + 32

        weather_data = {
            "temperature": round(temp_f, 1),
            "weather_code": current["weathercode"],
            "windspeed": current["windspeed"],
            "precipitation_probability": hourly["precipitation_probability"][0]
            if hourly["precipitation_probability"]
            else 0,
            "location": f"Zipcode location",
        }

        return weather_data, None

    except Exception as e:
        return None, "Weather data unavailable. Please try again."


def get_weather_description(code: int) -> str:
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Thunderstorm with heavy hail",
    }
    return descriptions.get(code, "Unknown conditions")


def get_clothing_recommendations(weather: Dict, preferences: Dict) -> List[str]:
    temp = weather["temperature"]
    weather_code = weather["weather_code"]
    precip_prob = weather["precipitation_probability"]

    recommendations = []

    if temp < 40:
        recommendations.extend(["Heavy coat", "Hat, gloves, scarf", "Warm layers"])
    elif temp < 55:
        recommendations.extend(["Medium jacket or coat", "Sweater"])
    elif temp < 65:
        recommendations.extend(["Light jacket or sweater"])
    elif temp < 75:
        recommendations.extend(["T-shirt with light layer"])
    else:
        recommendations.extend(["Light, breathable clothing"])

    if weather_code >= 51 and weather_code <= 82:
        recommendations.append("Waterproof jacket")
        recommendations.append("Umbrella")
    elif weather_code >= 71 and weather_code <= 86:
        recommendations.append("Heavy waterproof boots")
        recommendations.append("Warm layers")

    pref_clothing = preferences.get("clothing", {})
    if pref_clothing:
        weighted_recs = []
        for rec in recommendations:
            weight = pref_clothing.get(rec, 0)
            if weight >= 0:
                weighted_recs.extend([rec] * (weight + 1))
        recommendations = list(dict.fromkeys(weighted_recs))

    return recommendations[:5]


def get_activity_recommendations(weather: Dict, preferences: Dict) -> List[str]:
    temp = weather["temperature"]
    weather_code = weather["weather_code"]

    activities = []

    pref_activities = preferences.get("activities", {})

    is_marginal_weather = 45 <= temp <= 55 and weather_code <= 3

    if 65 <= temp <= 80 and weather_code <= 3:
        activities.extend(
            [
                "Outdoor hiking",
                "Biking",
                "Visit parks",
                "Beach activities",
                "Outdoor sports",
            ]
        )
    elif 50 <= temp < 65 and weather_code <= 3:
        activities.extend(["Walking", "Jogging", "Outdoor dining"])
    elif weather_code < 50:
        activities.extend(
            ["Shopping", "Visit museums", "Coffee shops", "Leisurely walks"]
        )
    elif weather_code >= 51 and weather_code <= 82:
        activities.extend(
            [
                "Indoor activities",
                "Visit museums",
                "Shopping centers",
                "Movies",
                "Cafes",
            ]
        )
    elif weather_code >= 71 and weather_code <= 86:
        activities.extend(
            [
                "Indoor activities",
                "Visit nearby locations",
                "Limited outdoor time",
                "Museums",
            ]
        )

    if is_marginal_weather and pref_activities:
        all_possible_activities = [
            "Outdoor hiking",
            "Biking",
            "Visit parks",
            "Beach activities",
            "Outdoor sports",
            "Walking",
            "Jogging",
            "Outdoor dining",
            "Shopping",
            "Visit museums",
            "Coffee shops",
            "Leisurely walks",
            "Indoor activities",
            "Shopping centers",
            "Movies",
            "Cafes",
            "Visit nearby locations",
            "Limited outdoor time",
        ]

        for act in all_possible_activities:
            weight = pref_activities.get(act, 0)
            if weight >= 2:
                activities.append(act)

    if pref_activities:
        weighted_acts = []
        for act in activities:
            weight = pref_activities.get(act, 0)
            if weight >= 0:
                weighted_acts.extend([act] * (weight + 1))
        activities = list(dict.fromkeys(weighted_acts))

    return activities[:5]


def get_commute_recommendations(
    weather: Dict, preferences: Dict
) -> Optional[List[str]]:
    precip_prob = weather["precipitation_probability"]
    weather_code = weather["weather_code"]

    if precip_prob <= 50 and weather_code < 51:
        return None

    recommendations = []

    if 51 <= weather_code <= 82:
        recommendations.extend(
            ["Allow extra time for slower driving", "Consider using public transit"]
        )
    elif 71 <= weather_code <= 86:
        recommendations.extend(
            [
                "Avoid non-essential travel",
                "Use snow tires if driving",
                "Check road conditions",
            ]
        )

    pref_commute = preferences.get("commute", {})
    if pref_commute:
        weighted_recs = []
        for rec in recommendations:
            weight = pref_commute.get(rec, 0)
            if weight >= 0:
                weighted_recs.extend([rec] * (weight + 1))
        recommendations = list(dict.fromkeys(weighted_recs))

    return list(dict.fromkeys(recommendations))[:3]


def format_output(
    weather: Dict,
    clothing: List[str],
    activities: List[str],
    commute: Optional[List[str]],
    zipcode: str,
) -> str:
    output = []

    location_info = f"Zipcode {zipcode}"

    output.append(f"🌤️ CURRENT CONDITIONS IN {location_info}")
    output.append("")
    output.append(f"Temperature: {weather['temperature']}°F")
    output.append(f"Conditions: {get_weather_description(weather['weather_code'])}")
    output.append("")

    output.append("👕 CLOTHING SUGGESTIONS")
    output.append("")
    for item in clothing:
        output.append(f"• {item}")
    output.append("")

    output.append("🏃 ACTIVITIES TO CONSIDER")
    output.append("")
    for activity in activities:
        output.append(f"• {activity}")
    output.append("")

    if commute:
        output.append("🚗 COMMUTE ADVICE")
        output.append("")
        for rec in commute:
            output.append(f"• {rec}")

    return "\n".join(output)


def process_feedback(category: str, item: str, feedback: str):
    preferences = load_preferences()

    if category not in preferences:
        preferences[category] = {}

    if feedback == "up":
        preferences[category][item] = preferences[category].get(item, 0) + 1
    elif feedback == "down":
        preferences[category][item] = preferences[category].get(item, 0) - 1

    save_preferences(preferences)
    return (
        "Feedback recorded. Your preferences will be used for future recommendations."
    )


def get_weather_recommendations(zipcode: str) -> str:
    valid, valid_zipcode, error = validate_zipcode(zipcode)
    if not valid:
        return error

    lat, lon, error = convert_zipcode_to_coordinates(valid_zipcode)
    if error:
        return error

    weather, error = fetch_weather(lat, lon)
    if error:
        return error

    preferences = load_preferences()

    clothing = get_clothing_recommendations(weather, preferences)
    activities = get_activity_recommendations(weather, preferences)
    commute = get_commute_recommendations(weather, preferences)

    return format_output(weather, clothing, activities, commute, zipcode)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python weather.py <zipcode> [--feedback <up|down> <category> <item>]"
        )
        sys.exit(1)

    if sys.argv[1] == "--feedback":
        if len(sys.argv) < 5:
            print("Usage: python weather.py --feedback <up|down> <category> <item>")
            sys.exit(1)
        feedback = sys.argv[2]
        category = sys.argv[3]
        item = sys.argv[4]
        result = process_feedback(category, item, feedback)
        print(result)
    else:
        zipcode = sys.argv[1]
        result = get_weather_recommendations(zipcode)
        print(result)
