import os
from datetime import datetime, timedelta
import urllib.parse
import requests
from dotenv import load_dotenv
from exceptions import WeatherAPIError

load_dotenv()

API_KEY = os.environ.get("TOMMOROW_WEATHER_API_KEY")


class Weather():
    def __init__(self, location, time, temperature, humidity, wind):
        self.location = location
        self.time = time
        self.temperature = temperature
        self.humidity = humidity
        self.wind = wind


def grab_forecast_by_city(city):
    encoded_city = urllib.parse.quote(city)
    url = f"https://api.tomorrow.io/v4/weather/forecast?location={encoded_city}&apikey={API_KEY}"

    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers, timeout=4)
    response_json = response.json()

    if response.status_code == 200:
        return response_json

    raise WeatherAPIError(response_json["message"], response.status_code)


def parse_weather_data_by_city(city):
    try:
        data = grab_forecast_by_city(city)
    except WeatherAPIError as e:
        return e

    hourly = data["timelines"]["hourly"]
    location = data["location"]["name"]

    def create_weather_object(values, location, time):
        temp = values["temperature"]
        humi = values["humidity"]
        wind = values["windSpeed"]
        return Weather(location, time, temp, humi, wind)

    next_hour = create_weather_object(hourly[2]["values"], datetime.strptime(
        hourly[2]["time"], "%Y-%m-%dT%H:%M:%SZ"), location)

    print(next_hour.location)
    print(next_hour.time)
    print(next_hour.temperature)
    print(next_hour.wind)


parse_weather_data_by_city("neuhäsen")
