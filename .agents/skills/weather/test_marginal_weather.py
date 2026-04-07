#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from weather import get_weather_recommendations, weather as weather_module

# Mock: 50°F, overcast (weather_code=3) - marginal weather
weather_50_overcast = {
    "temperature": 50.0,
    "weather_code": 3,  # Overcast
    "precipitation_probability": 20,
    "location": "Test location",
}

# Save original
original_fetch = weather_module.fetch_weather


def mock_fetch_weather(lat, lon):
    return weather_50_overcast, None


weather_module.fetch_weather = mock_fetch_weather

# Load preferences with outdoor activity weights
import json
from weather import PREFERENCES_FILE

with open(PREFERENCES_FILE, "r") as f:
    print("Current preferences:")
    print(f.read())

print("\n" + "=" * 60)
print("TEST: 50°F Overcast (marginal weather)")
print("=" * 60)

result = get_weather_recommendations("94103")
print(result)

# Test with clear preferences removed
print("\n" + "=" * 60)
print("CONTROL: Same weather WITHOUT preferences")
print("=" * 60)

import shutil

shutil.copy(PREFERENCES_FILE, PREFERENCES_FILE + ".test_bak")
os.remove(PREFERENCES_FILE)

result_no_pref = get_weather_recommendations("94103")
print(result_no_pref)

shutil.copy(PREFERENCES_FILE + ".test_bak", PREFERENCES_FILE)
os.remove(PREFERENCES_FILE + ".test_bak")
