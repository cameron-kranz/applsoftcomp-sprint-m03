---
name: weather
description: Provide personalized daily recommendations based on current weather conditions. Users specify location via zipcode and receive clothing suggestions, activity ideas, and commute advice (when relevant).
---

## Workflow

This skill provides personalized weather-based recommendations through the following steps:

### Step 1: Receive User Input
Accept a zipcode from the user. This should be a US zipcode in the format "12345".

### Step 2: Validate Zipcode
Validate the user input:
- Check if input is exactly 5 digits
- Check if input contains only numeric characters
- If invalid, return error message: "Please enter a valid 5-digit US zipcode"
- If valid, proceed to next step

### Step 3: Convert Zipcode to Coordinates
Convert the zipcode to latitude and longitude coordinates:
- Use OpenStreetMap's Nominatim API (free, no API key)
- Query format: https://nominatim.openstreetmap.org/search?postalcode={ZIPCODE}&format=json&country=US
- Parse response to get lat and lon
- If no results found, return error: "Could not find location for that zipcode"
- If request fails, return error: "Unable to look up location. Please try again."

### Step 4: Fetch Current Weather
Retrieve current weather conditions:
- Use Open-Meteo API (free, no API key required)
- Query format: https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true&hourly=precipitation_probability,precipitation,windspeed_10m
- Extract current conditions:
  - Temperature (°F converted from °C)
  - Weather code (for conditions description)
  - Precipitation probability
  - Wind speed
- If API call fails, return error: "Weather data unavailable. Please try again."

### Step 5: Parse Weather Conditions
Convert weather code to description:
- 0: Clear sky
- 1-3: Partly cloudy
- 45-48: Foggy
- 51-67: Rainy
- 71-77: Snowy
- 80-82: Showers
- 95-99: Thunderstorm

### Step 6: Generate Initial Recommendations
Based on weather conditions, generate recommendations:

**Clothing Rules:**
- Temp < 40°F: Heavy coat, hat, gloves, scarf
- Temp 40-55°F: Medium jacket or coat, sweater
- Temp 55-65°F: Light jacket or sweater
- Temp 65-75°F: T-shirt with light layer
- Temp > 75°F: Light, breathable clothing
- Raining: Waterproof jacket, umbrella
- Snowing: Heavy waterproof boots, warm layers

**Activity Rules:**
- Sunny & 65-80°F: Outdoor hiking, biking, parks, beach, sports
- Sunny & 50-65°F: Walking, jogging, outdoor dining
- Cloudy/mild: Shopping, museums, coffee shops, walking
- Rain: Indoor activities, museums, shopping centers, movies
- Snow: Limited outdoor time, indoor activities, nearby locations

**Commute Rules:**
- Include if precipitation_probability > 50% or weather code indicates rain/snow
- Rain: Allow extra time for slower driving, consider public transit
- Snow: Avoid non-essential travel, use snow tires if driving

### Step 7: Apply Learned Preferences
Check for stored preferences file:
- If `weather_preferences.json` exists, read it
- Apply preference weights to standard recommendations:
  - Positive weights: increase likelihood/visibility of those options
  - Negative weights: decrease likelihood/remove those options
- If no preferences file, use standard rules only

### Step 8: Format and Output Recommendations
Format output with clear sections and conversational tone:

```
🌤️ CURRENT CONDITIONS IN [City/Zipcode]

Temperature: [X]°F
Conditions: [sunny/cloudy/rainy/etc.]

👕 CLOTHING SUGGESTIONS

• [clothing option 1]
• [clothing option 2]
• [clothing option 3]

🏃 ACTIVITIES TO CONSIDER

• [activity 1]
• [activity 2]
• [activity 3]

[🚗 COMMUTE ADVICE if applicable]
```

If rain or snow, add:
```
🚗 COMMUTE ADVICE

• [commute suggestion 1]
• [commute suggestion 2]
```

Use emojis sparingly and appropriately. Maintain friendly, conversational tone.

### Step 9: Handle User Feedback
If user provides feedback (thumbs up/down):
- Store feedback in `weather_preferences.json`
- Format: JSON with categories for clothing, activities, commute
- Adjust weights: +1 for thumbs up, -1 for thumbs down
- Example:
```json
{
  "clothing": {
    "light jacket": 1,
    "heavy coat": -1
  },
  "activities": {
    "outdoor hiking": 2,
    "indoor museums": -1
  },
  "commute": {
    "public transit": 1
  }
}
```

### Error Handling
Return clear error messages for:
- Invalid zipcode format
- Zipcode not found
- Weather API unavailable
- Geocoding service unavailable

Always maintain user-friendly, conversational tone in error messages.