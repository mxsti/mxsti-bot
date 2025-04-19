""" helper functions to interact with tomorrow weather api """

import os
from datetime import datetime
from dataclasses import dataclass
import urllib.parse
import requests
from dotenv import load_dotenv
from utils.exceptions import APIError

load_dotenv()

API_KEY = os.environ.get("TOMMOROW_WEATHER_API_KEY")


@dataclass
class Weather():
    """
    Class containing weather metadata
    """
    location: str = None
    time: datetime = None
    weather_code: int = None


@dataclass
class WeatherToday():
    """
    Class containing todays weather information
    """
    metadata: Weather = None
    temperature: float = None
    humidity: str = None
    wind: str = None


@dataclass
class WeatherTomorrow:
    """
    Class containing tomorrows weather information
    """
    metadata: Weather = None
    temperature_max: float = None
    temperature_min: float = None
    temperature_avg: float = None
    sunrise_time: datetime = None
    sunset_time: datetime = None


def grab_forecast_by_city(location):
    """
    Calls the Weather API (api.tomorrow.io) and grabs a weather forecast

    Parameters:
        location - location string defining for where the api should get the weather for

    Returns:
        response JSON from the weather api
    """
    encoded_city = urllib.parse.quote(location)
    url = f"https://api.tomorrow.io/v4/weather/forecast?location={encoded_city}&apikey={API_KEY}"

    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers, timeout=4)
    response_json = response.json()

    if response.status_code == 200:
        return response_json

    raise APIError(response_json["message"], response.status_code)


def parse_weather_data_by_location_today(location_input):
    """
    Parses the response json from the weather api and puts it in the weather class

    Parameters:
        location_input - location string defining for where the api should get the weather for

    Returns:
        array - array containing 4 weather objects with the forecast for the next 6 hours
    """
    try:
        data = grab_forecast_by_city(location_input)
    except APIError as e:
        return e

    hourly = data["timelines"]["hourly"]
    location = data["location"]["name"]

    def create_weather_object(values, location, time):
        temp = values["temperature"]
        humi = values["humidity"]
        wind = values["windSpeed"]
        weather_code = values["weatherCode"]
        return WeatherToday(
            metadata=Weather(location=location, time=datetime.strftime(
                time, "%d.%m. %H:%M Uhr"), weather_code=weather_code),
            temperature=temp,
            humidity=humi,
            wind=wind)

    next_hour = create_weather_object(hourly[2]["values"], location, datetime.strptime(
        hourly[2]["time"], "%Y-%m-%dT%H:%M:%SZ"))

    two_hours = create_weather_object(hourly[4]["values"], location, datetime.strptime(
        hourly[4]["time"], "%Y-%m-%dT%H:%M:%SZ"))

    fours_hours = create_weather_object(hourly[6]["values"], location, datetime.strptime(
        hourly[6]["time"], "%Y-%m-%dT%H:%M:%SZ"))

    six_hours = create_weather_object(hourly[8]["values"], location, datetime.strptime(
        hourly[8]["time"], "%Y-%m-%dT%H:%M:%SZ"))

    return [next_hour, two_hours, fours_hours, six_hours]


def parse_weather_data_by_location_tomorrow(location_input):
    """
    Parses the response json from the weather api and puts it in the weather class

    Parameters:
        location_input - location string defining for where the api should get the weather for

    Returns:
        weather - weather object containing weather forecast for the upcoming day
    """
    try:
        data = grab_forecast_by_city(location_input)
    except APIError as e:
        return e

    daily = data["timelines"]["daily"]
    location = data["location"]["name"]

    def create_weather_object(values, location, time):
        temp_max = values["temperatureMax"]
        temp_min = values["temperatureMin"]
        temp_avg = values["temperatureAvg"]
        weather_code = values["weatherCodeMax"]
        sunrise = datetime.strptime(
            values["sunriseTime"], "%Y-%m-%dT%H:%M:%SZ")
        sunset = datetime.strptime(values["sunsetTime"], "%Y-%m-%dT%H:%M:%SZ")
        return WeatherTomorrow(
            metadata=Weather(location=location, time=datetime.strftime(
                time, "%d.%m.%Y "), weather_code=weather_code),
            temperature_max=temp_max,
            temperature_min=temp_min,
            temperature_avg=temp_avg,
            sunrise_time=datetime.strftime(sunrise, "%H:%M Uhr"),
            sunset_time=datetime.strftime(sunset, "%H:%M Uhr"),)

    return create_weather_object(daily[1]["values"], location, datetime.strptime(
        daily[1]["time"], "%Y-%m-%dT%H:%M:%SZ"))
