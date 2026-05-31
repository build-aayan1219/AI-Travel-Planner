# ============================================================
#  utils/weather.py
#  All weather-related functions using OpenWeatherMap API
# ============================================================

import requests
import os
from dotenv import load_dotenv

load_dotenv()
WEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")

# Weather condition to emoji mapping
WEATHER_EMOJI = {
    "Clear": "☀️",
    "Clouds": "⛅",
    "Rain": "🌧️",
    "Drizzle": "🌦️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Fog": "🌫️",
    "Haze": "🌫️",
    "Dust": "🌪️",
    "Smoke": "💨",
    "Tornado": "🌪️"
}

# Travel tip based on weather
WEATHER_TIPS = {
    "Clear": "🕶️ Great weather! Carry sunscreen and sunglasses.",
    "Clouds": "🌤️ Pleasant weather. Good for outdoor activities.",
    "Rain": "☂️ Carry a raincoat or umbrella. Wear waterproof footwear.",
    "Drizzle": "🌂 Light rain expected. Keep an umbrella handy.",
    "Thunderstorm": "⚠️ Avoid outdoor activities. Stay indoors if possible.",
    "Snow": "🧥 Bundle up! Wear warm layers and waterproof boots.",
    "Mist": "👁️ Low visibility. Drive carefully if renting vehicles.",
    "Fog": "👁️ Low visibility. Drive carefully if renting vehicles.",
    "Haze": "😷 Air quality may be poor. Consider a mask.",
}


def get_current_weather(city: str) -> dict:
    """
    Fetches current weather for a city.
    Returns a dictionary with all weather details.
    """
    if not WEATHER_KEY:
        return {"error": "No OPENWEATHER_API_KEY found in .env file."}

    try:
        url = (
            f"http://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={WEATHER_KEY}&units=metric"
        )
        response = requests.get(url, timeout=8)
        data = response.json()

        if data.get("cod") != 200:
            return {"error": f"City '{city}' not found. Try spelling it in English."}

        condition = data["weather"][0]["main"]

        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temp": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "temp_min": round(data["main"]["temp_min"]),
            "temp_max": round(data["main"]["temp_max"]),
            "humidity": data["main"]["humidity"],
            "wind_speed": round(data["wind"]["speed"] * 3.6),  # Convert m/s to km/h
            "description": data["weather"][0]["description"].capitalize(),
            "condition": condition,
            "emoji": WEATHER_EMOJI.get(condition, "🌡️"),
            "tip": WEATHER_TIPS.get(condition, "Check the weather before heading out."),
            "visibility": round(data.get("visibility", 10000) / 1000, 1),  # Convert m to km
        }

    except requests.exceptions.ConnectionError:
        return {"error": "No internet connection. Check your network."}
    except requests.exceptions.Timeout:
        return {"error": "Weather service timed out. Try again."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def get_forecast(city: str, days: int = 5) -> dict:
    """
    Fetches a 5-day weather forecast for a city.
    Returns forecast data grouped by day.
    """
    if not WEATHER_KEY:
        return {"error": "No OPENWEATHER_API_KEY found in .env file."}

    try:
        url = (
            f"http://api.openweathermap.org/data/2.5/forecast"
            f"?q={city}&appid={WEATHER_KEY}&units=metric&cnt={days * 8}"
        )
        response = requests.get(url, timeout=8)
        data = response.json()

        if data.get("cod") != "200":
            return {"error": f"Could not get forecast for '{city}'."}

        # Group forecast by day (API returns data every 3 hours)
        forecast_by_day = {}
        for item in data["list"]:
            day = item["dt_txt"].split(" ")[0]  # Get just the date part
            if day not in forecast_by_day:
                forecast_by_day[day] = []
            forecast_by_day[day].append({
                "time": item["dt_txt"].split(" ")[1][:5],
                "temp": round(item["main"]["temp"]),
                "description": item["weather"][0]["description"].capitalize(),
                "emoji": WEATHER_EMOJI.get(item["weather"][0]["main"], "🌡️"),
                "humidity": item["main"]["humidity"],
            })

        return {
            "city": data["city"]["name"],
            "country": data["city"]["country"],
            "forecast": forecast_by_day
        }

    except Exception as e:
        return {"error": str(e)}


def get_best_travel_months(city: str) -> str:
    """
    Returns a simple guide on best months to visit a city.
    This is static data for popular Indian destinations.
    """
    travel_calendar = {
        "goa": "🏖️ Best: November–February (dry & pleasant). Avoid June–September (heavy monsoon).",
        "manali": "🏔️ Best: March–June (snow activities) & October (scenic). Avoid Jan–Feb (roads may close).",
        "jaipur": "🏰 Best: October–March (cool & dry). Avoid April–June (very hot, 40°C+).",
        "kerala": "🌴 Best: September–March. Avoid June–August (heavy monsoon in most areas).",
        "mumbai": "🌊 Best: November–February (cool). Avoid June–September (heavy monsoon).",
        "delhi": "🕌 Best: October–March (cool). Avoid May–July (extreme heat up to 45°C).",
        "ooty": "🌿 Best: April–June & September–November. Avoid Jan–Feb (too cold) & Monsoon.",
        "shimla": "❄️ Best: March–June (pleasant) & Dec–Feb (snowfall). Avoid monsoon (landslide risk).",
        "agra": "🕌 Best: October–March. Avoid summer (extreme heat makes outdoor visits tough).",
        "leh": "🏔️ Best: June–September only. Roads closed rest of the year.",
    }

    city_lower = city.lower().strip()
    for key, info in travel_calendar.items():
        if key in city_lower or city_lower in key:
            return info

    return f"🗓️ Research the best season for {city} — weather varies by region in India."