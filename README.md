# 🌦️ Day 02: Weather App CLI (Learning Free APIs)

A Python command-line weather application built to learn how to interact with free REST APIs using Python and the `requests` library.

---

## 🎯 What You Will Learn

1. **What is a REST API?**
   - How your Python code talks to remote servers over HTTP.
2. **Anatomy of an HTTP Request:**
   - **Base URL:** `https://api.weatherapi.com/v1`
   - **Endpoints:** `/current.json` (current weather) or `/forecast.json` (multi-day forecast)
   - **Query Parameters:** `?key=YOUR_KEY&q=London&days=3`
3. **API Key Authentication & Security:**
   - Why API keys are used to identify and rate-limit clients.
   - Storing secrets safely in `.env` and ignoring them in `.gitignore`.
4. **HTTP Status Codes & Error Handling:**
   - `200 OK`: Request succeeded.
   - `400 Bad Request`: Location not found or missing parameters.
   - `401 / 403 Unauthorized`: Invalid or missing API key.
   - Handling network failures and timeouts with `try/except`.

---

## 🚀 Quick Start

### 1. Activate the Virtual Environment
A virtual environment `.venv` is already configured in this workspace:
```bash
source .venv/bin/activate
```

*(If you ever need to re-create it: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`)*

---

### 2. Try the Demo (No API Key Required!)
Before signing up, you can test the CLI interface immediately with mock data:
```bash
python weather.py --demo
```

---

### 3. Get Your Free WeatherAPI Key (1 Minute)

1. Open [WeatherAPI Signup](https://www.weatherapi.com/signup.aspx) in your browser.
2. Sign up with an email and password (it is free, no credit card required).
3. Verify your email and log in to your dashboard.
4. Copy your **API Key**.
5. Open the `.env` file in this directory and paste your key:
   ```env
   WEATHER_API_KEY=your_actual_api_key_here
   ```

---

### 4. Running the App with Live API Data

**Interactive Mode:**
```bash
python weather.py
```
*(Prompts you for a city name)*

**Pass City as Argument:**
```bash
python weather.py Tokyo
python weather.py "New York"
```

**Include 3-Day Forecast:**
```bash
python weather.py London --forecast
# or using short flag:
python weather.py London -f
```

**Switch to Fahrenheit:**
```bash
python weather.py "Los Angeles" --unit F
```

---

## 🔍 How the Code Works (Step-by-Step)

### 1. Loading Environment Variables
```python
from dotenv import load_dotenv
import os

load_dotenv()  # reads .env file
api_key = os.getenv("WEATHER_API_KEY")
```
This keeps your secret API key outside of git-versioned code.

### 2. Making the Request
```python
import requests

url = "https://api.weatherapi.com/v1/current.json"
params = {
    "key": api_key,
    "q": "Kathmandu",
    "aqi": "no"
}

response = requests.get(url, params=params, timeout=10)
```
The `requests` library automatically builds the URL:
`https://api.weatherapi.com/v1/current.json?key=...&q=Kathmandu&aqi=no`

### 3. Parsing the JSON Response
```python
data = response.json()
temperature = data["current"]["temp_c"]
condition = data["current"]["condition"]["text"]
```
Python automatically converts the server's JSON payload into standard Python dictionaries and lists.

