#!/usr/bin/env python3
"""
Day 02: Weather App CLI
A terminal weather application demonstrating how to consume REST APIs using Python & requests.
Supported Providers:
  1. WeatherAPI.com (requires free API key from weatherapi.com)
  2. OpenWeatherMap (requires free API key from openweathermap.org)
  3. Open-Meteo (100% free, NO key required - instant start)
"""

import os
import sys
import argparse
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

WEATHERAPI_BASE = "https://api.weatherapi.com/v1"
OPENWEATHER_BASE = "https://api.openweathermap.org/data/2.5"
OPENMETEO_GEO_BASE = "https://geocoding-api.open-meteo.com/v1"
OPENMETEO_WEATHER_BASE = "https://api.open-meteo.com/v1"

# WMO Weather interpretation codes (WW) for Open-Meteo
WMO_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    61: ("Slight rain", "🌦️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    71: ("Slight snow fall", "🌨️"),
    73: ("Moderate snow fall", "❄️"),
    75: ("Heavy snow fall", "❄️"),
    80: ("Slight rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌧️"),
    82: ("Violent rain showers", "⛈️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with hail", "⛈️"),
}

WEATHER_EMOJIS = {
    "sunny": "☀️",
    "clear": "☀️",
    "partly cloudy": "⛅",
    "cloudy": "☁️",
    "overcast": "☁️",
    "mist": "🌫️",
    "fog": "🌫️",
    "rain": "🌧️",
    "patchy rain": "🌦️",
    "light rain": "🌦️",
    "moderate rain": "🌧️",
    "heavy rain": "🌧️",
    "thunder": "⛈️",
    "snow": "❄️",
    "windy": "💨",
}


def get_weather_emoji(condition_text: str, is_day: int = 1) -> str:
    lower_cond = condition_text.lower().strip()
    if lower_cond == "clear" and is_day == 0:
        return "🌙"
    for key, emoji in WEATHER_EMOJIS.items():
        if key in lower_cond:
            return emoji
    return "🌤️"


# ==========================================
# 1. WeatherAPI.com Implementation
# ==========================================
def fetch_from_weatherapi(city: str, api_key: str, forecast: bool = False) -> dict:
    endpoint = "forecast.json" if forecast else "current.json"
    url = f"{WEATHERAPI_BASE}/{endpoint}"
    params = {"key": api_key, "q": city, "aqi": "no"}
    if forecast:
        params["days"] = 3

    response = requests.get(url, params=params, timeout=10)

    if response.status_code == 200:
        raw = response.json()
        loc = raw.get("location", {})
        curr = raw.get("current", {})
        cond = curr.get("condition", {})

        forecast_list = []
        for item in raw.get("forecast", {}).get("forecastday", []):
            d = item.get("day", {})
            forecast_list.append({
                "date": item.get("date", ""),
                "condition": d.get("condition", {}).get("text", "N/A"),
                "emoji": get_weather_emoji(d.get("condition", {}).get("text", "")),
                "min_c": d.get("mintemp_c", 0),
                "max_c": d.get("maxtemp_c", 0),
                "rain_prob": d.get("daily_chance_of_rain", 0),
            })

        return {
            "provider": "WeatherAPI.com",
            "city": loc.get("name", city),
            "country": loc.get("country", ""),
            "localtime": loc.get("localtime", "N/A"),
            "condition": cond.get("text", "N/A"),
            "emoji": get_weather_emoji(cond.get("text", ""), curr.get("is_day", 1)),
            "temp_c": curr.get("temp_c"),
            "temp_f": curr.get("temp_f"),
            "feelslike_c": curr.get("feelslike_c"),
            "feelslike_f": curr.get("feelslike_f"),
            "humidity": curr.get("humidity"),
            "wind_kph": curr.get("wind_kph"),
            "wind_dir": curr.get("wind_dir"),
            "pressure_mb": curr.get("pressure_mb"),
            "uv": curr.get("uv"),
            "forecast": forecast_list,
        }

    err_msg = ""
    try:
        err_msg = response.json().get("error", {}).get("message", response.text)
    except Exception:
        err_msg = response.text

    if response.status_code in (401, 403):
        raise PermissionError(f"WeatherAPI Authentication Error: {err_msg}")
    elif response.status_code == 400:
        raise ValueError(f"WeatherAPI Location Error: {err_msg}")
    else:
        response.raise_for_status()


# ==========================================
# 2. OpenWeatherMap Implementation
# ==========================================
def fetch_from_openweathermap(city: str, api_key: str) -> dict:
    url = f"{OPENWEATHER_BASE}/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}

    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        raw = response.json()
        main = raw.get("main", {})
        weather0 = raw.get("weather", [{}])[0]
        wind = raw.get("wind", {})
        sys_data = raw.get("sys", {})

        temp_c = main.get("temp", 0)
        temp_f = (temp_c * 9/5) + 32
        feels_c = main.get("feels_like", 0)
        feels_f = (feels_c * 9/5) + 32
        wind_speed_kph = round(wind.get("speed", 0) * 3.6, 1)

        cond_text = weather0.get("main", "N/A")
        return {
            "provider": "OpenWeatherMap.org",
            "city": raw.get("name", city),
            "country": sys_data.get("country", ""),
            "localtime": "Live",
            "condition": f"{cond_text} ({weather0.get('description', '')})",
            "emoji": get_weather_emoji(cond_text),
            "temp_c": temp_c,
            "temp_f": round(temp_f, 1),
            "feelslike_c": feels_c,
            "feelslike_f": round(feels_f, 1),
            "humidity": main.get("humidity"),
            "wind_kph": wind_speed_kph,
            "wind_dir": str(wind.get("deg", "")) + "°",
            "pressure_mb": main.get("pressure"),
            "uv": "N/A",
            "forecast": [],
        }

    err_msg = ""
    try:
        err_msg = response.json().get("message", response.text)
    except Exception:
        err_msg = response.text

    if response.status_code == 401:
        raise PermissionError(f"OpenWeatherMap Key Error: {err_msg}")
    elif response.status_code == 404:
        raise ValueError(f"City '{city}' not found on OpenWeatherMap.")
    else:
        response.raise_for_status()


# ==========================================
# 3. Open-Meteo (Zero Key Required!)
# ==========================================
def fetch_from_open_meteo(city: str, forecast: bool = False) -> dict:
    """Uses Open-Meteo geocoding + forecast API. Requires NO API key."""
    # Step 1: Geocode city name to lat/lon
    geo_url = f"{OPENMETEO_GEO_BASE}/search"
    geo_resp = requests.get(geo_url, params={"name": city, "count": 1}, timeout=10)
    geo_resp.raise_for_status()
    geo_data = geo_resp.json()

    results = geo_data.get("results")
    if not results:
        raise ValueError(f"City '{city}' not found.")

    place = results[0]
    lat = place.get("latitude")
    lon = place.get("longitude")
    resolved_name = place.get("name", city)
    country = place.get("country", "")

    # Step 2: Fetch weather for coordinates
    w_url = f"{OPENMETEO_WEATHER_BASE}/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "timezone": "auto",
        "hourly": ["relativehumidity_2m", "surface_pressure"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "weathercode", "precipitation_probability_max"]
    }
    w_resp = requests.get(w_url, params=params, timeout=10)
    w_resp.raise_for_status()
    w_data = w_resp.json()

    curr = w_data.get("current_weather", {})
    code = curr.get("weathercode", 0)
    cond_desc, emoji = WMO_CODES.get(code, ("Fair", "🌤️"))

    temp_c = curr.get("temperature", 0)
    temp_f = round((temp_c * 9/5) + 32, 1)

    # Extract humidity and pressure if available
    humidity = w_data.get("hourly", {}).get("relativehumidity_2m", [None])[0]
    pressure = w_data.get("hourly", {}).get("surface_pressure", [None])[0]

    # Forecast days
    forecast_list = []
    if forecast and "daily" in w_data:
        daily = w_data["daily"]
        times = daily.get("time", [])[:3]
        maxs = daily.get("temperature_2m_max", [])[:3]
        mins = daily.get("temperature_2m_min", [])[:3]
        codes = daily.get("weathercode", [])[:3]
        rains = daily.get("precipitation_probability_max", [])[:3]

        for i in range(len(times)):
            c_desc, c_emoji = WMO_CODES.get(codes[i], ("Fair", "🌤️"))
            forecast_list.append({
                "date": times[i],
                "condition": c_desc,
                "emoji": c_emoji,
                "min_c": mins[i],
                "max_c": maxs[i],
                "rain_prob": rains[i] if i < len(rains) else 0,
            })

    return {
        "provider": "Open-Meteo (No Key Needed)",
        "city": resolved_name,
        "country": country,
        "localtime": curr.get("time", "N/A"),
        "condition": cond_desc,
        "emoji": emoji,
        "temp_c": temp_c,
        "temp_f": temp_f,
        "feelslike_c": temp_c,
        "feelslike_f": temp_f,
        "humidity": humidity if humidity is not None else "N/A",
        "wind_kph": curr.get("windspeed", 0),
        "wind_dir": f"{curr.get('winddirection', 0)}°",
        "pressure_mb": pressure if pressure is not None else "N/A",
        "uv": "N/A",
        "forecast": forecast_list,
    }


def display_weather(data: dict, unit: str = "C"):
    unit_symbol = "°C" if unit == "C" else "°F"
    temp = data["temp_c"] if unit == "C" else data["temp_f"]
    feels = data["feelslike_c"] if unit == "C" else data["feelslike_f"]

    print("\n" + "─" * 48)
    print(f" 📍 Weather for {data['city']}, {data['country']}")
    print(f" 🕒 Local Time: {data['localtime']}  |  Provider: {data['provider']}")
    print("─" * 48)
    print(f" {data['emoji']}  Condition:    {data['condition']}")
    print(f" 🌡️  Temperature:  {temp}{unit_symbol} (Feels like {feels}{unit_symbol})")
    print(f" 💧 Humidity:     {data['humidity']}%")
    print(f" 💨 Wind:         {data['wind_kph']} km/h ({data['wind_dir']})")
    if data["uv"] != "N/A":
        print(f" ☀️  UV Index:     {data['uv']}")
    if data["pressure_mb"] != "N/A":
        print(f" 📊 Pressure:     {data['pressure_mb']} mb")
    print("─" * 48)

    forecast_days = data.get("forecast", [])
    if forecast_days:
        print("\n 📅 3-Day Forecast:")
        print(" ┌────────────┬────────────────────┬──────────────┬───────────┐")
        print(" │ Date       │ Condition          │ Temp (Min/Max│ Rain Prob │")
        print(" ├────────────┼────────────────────┼──────────────┼───────────┤")
        for item in forecast_days:
            cond_display = f"{item['emoji']} {item['condition']}"[:18]
            min_t = item['min_c'] if unit == "C" else round((item['min_c'] * 9/5) + 32, 1)
            max_t = item['max_c'] if unit == "C" else round((item['max_c'] * 9/5) + 32, 1)
            temp_range = f"{min_t:.0f}{unit_symbol} - {max_t:.0f}{unit_symbol}"
            print(f" │ {item['date']:<10} │ {cond_display:<18} │ {temp_range:<12} │ {item['rain_prob']:>7}% │")
        print(" └────────────┴────────────────────┴──────────────┴───────────┘\n")


def diagnose_and_fetch(city: str, api_key: str, forecast: bool, unit: str):
    """
    Intelligently attempts WeatherAPI, checks OpenWeatherMap,
    and falls back to Open-Meteo if credentials fail.
    """
    print(f"\n📡 Requesting weather data for '{city}'...")

    # 1. Try WeatherAPI.com
    if api_key and api_key != "your_weatherapi_key_here":
        try:
            data = fetch_from_weatherapi(city, api_key, forecast=forecast)
            display_weather(data, unit=unit)
            return
        except PermissionError as e:
            print(f"\n⚠️  WeatherAPI.com reported: {e}")
            print("👉 Checking if this is an OpenWeatherMap key...")

        # 2. Try OpenWeatherMap (often users register on OpenWeatherMap by mistake)
        try:
            data = fetch_from_openweathermap(city, api_key)
            print("\n🎉 Found valid OpenWeatherMap key!")
            display_weather(data, unit=unit)
            return
        except PermissionError:
            print("⚠️  OpenWeatherMap also reported key not ready or invalid.")
        except Exception:
            pass

    # 3. Fallback to Open-Meteo (100% Free, NO API key required!)
    print("\n💡 Showing live weather using Open-Meteo (Free API, no key required):")
    try:
        data = fetch_from_open_meteo(city, forecast=forecast)
        display_weather(data, unit=unit)
    except Exception as err:
        print(f"❌ Failed to fetch weather: {err}")


def main():
    parser = argparse.ArgumentParser(description="Day 02: Weather App CLI")
    parser.add_argument("city", nargs="?", help="City name (e.g. London, Tokyo, Kathmandu)")
    parser.add_argument("-f", "--forecast", action="store_true", help="Include 3-day forecast")
    parser.add_argument("-u", "--unit", choices=["C", "F"], default="C", help="Temperature unit: C or F")
    parser.add_argument("--open-meteo", action="store_true", help="Force using Open-Meteo (no key required)")

    args = parser.parse_args()
    api_key = os.getenv("WEATHER_API_KEY", "").strip()

    city = args.city
    if not city:
        city = input("🔍 Enter city name: ").strip()
        if not city:
            city = "Kathmandu"

    if args.open_meteo:
        data = fetch_from_open_meteo(city, forecast=args.forecast)
        display_weather(data, unit=args.unit)
        return

    diagnose_and_fetch(city, api_key, args.forecast, args.unit)


if __name__ == "__main__":
    main()
