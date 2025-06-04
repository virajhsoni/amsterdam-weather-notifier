import datetime
import requests
import os
import json

def get_next_monday():
    today = datetime.date.today()
    next_monday = today + datetime.timedelta(days=(7 - today.weekday()))
    return next_monday

def fetch_weather():
    lat, lon = 52.3676, 4.9041  # Amsterdam
    start_date = get_next_monday()
    end_date = start_date + datetime.timedelta(days=9)
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,"
        f"precipitation_probability_max,weathercode&timezone=auto"
        f"&start_date={start_date}&end_date={end_date}"
    )
    response = requests.get(url)
    return response.json(), start_date

def weather_code_to_text(code):
    mapping = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Rime fog", 51: "Light drizzle", 61: "Light rain",
        63: "Moderate rain", 65: "Heavy rain", 71: "Snow", 80: "Rain showers",
        95: "Thunderstorm"
    }
    return mapping.get(code, "Unknown")

def format_message(data, start_date):
    days = data['daily']['time']
    highs = data['daily']['temperature_2m_max']
    lows = data['daily']['temperature_2m_min']
    codes = data['daily']['weathercode']
    rain_chances = data['daily']['precipitation_probability_max']

    lines = ["🌤 10-Day Weather Forecast for Amsterdam (from next Monday):\n"]
    for i in range(10):
        date = datetime.datetime.strptime(days[i], "%Y-%m-%d").strftime("%a %d %b")
        summary = f"{date}: {highs[i]}°C / {lows[i]}°C, {weather_code_to_text(codes[i])}, 🌧 {rain_chances[i]}%"
        lines.append(summary)

    return "\n".join(lines)

def send_push(message):
    token = os.getenv("PUSHBULLET_TOKEN")
    data = {"type": "note", "title": "Amsterdam Weather", "body": message}
    resp = requests.post(
        "https://api.pushbullet.com/v2/pushes",
        data=json.dumps(data),
        headers={"Access-Token": token, "Content-Type": "application/json"}
    )
    if resp.status_code != 200:
        raise Exception(f"Pushbullet failed: {resp.text}")

def main():
    weather_data, start_date = fetch_weather()
    message = format_message(weather_data, start_date)
    send_push(message)

if __name__ == "__main__":
    main()
