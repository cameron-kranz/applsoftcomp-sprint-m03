#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test with marginal weather: 55°F, light drizzle (weather_code=51)
# Standard rules would push indoor activities due to rain code
# But user has positive weights on outdoor activities

# Create a test scenario
from weather import get_activity_recommendations, load_preferences
from weather import PREFERENCES_FILE

print("=" * 60)
print("SCENARIO 1: Light drizzle, 55°F with outdoor preferences")
print("=" * 60)

weather_rainy_marginal = {
    "temperature": 55.0,
    "weather_code": 51,  # Light drizzle
    "precipitation_probability": 60,
}

preferences = load_preferences()
print("Loaded preferences:")
print(preferences)

activities = get_activity_recommendations(weather_rainy_marginal, preferences)
print("\nActivities recommended:")
for a in activities:
    print(f"  • {a}")

print("\n" + "=" * 60)
print("SCENARIO 2: Same weather WITHOUT preferences")
print("=" * 60)

activities_no_pref = get_activity_recommendations(weather_rainy_marginal, {})
print("\nActivities recommended:")
for a in activities_no_pref:
    print(f"  • {a}")

print("\n" + "=" * 60)
print("COMPARISON")
print("=" * 60)
print(f"With outdoor preferences: {len(activities)} activities")
print(f"Without preferences: {len(activities_no_pref)} activities")

# Check if outdoor activities appear in both
outdoor_keywords = ["hiking", "biking", "walking", "jogging", "outdoor"]
with_outdoor = any(k in " ".join(activities).lower() for k in outdoor_keywords)
without_outdoor = any(
    k in " ".join(activities_no_pref).lower() for k in outdoor_keywords
)

print(f"\nOutdoor activities present WITH preferences: {with_outdoor}")
print(f"Outdoor activities present WITHOUT preferences: {without_outdoor}")
