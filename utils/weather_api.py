""" helper functions to interact with tomorrow weather api """

import os
from datetime import datetime
from dataclasses import dataclass
import urllib.parse
import requests
from dotenv import load_dotenv
from utils.exceptions import WeatherAPIError

load_dotenv()

API_KEY = os.environ.get("TOMMOROW_WEATHER_API_KEY")


@dataclass
class Weather():
    """
    Class containing weather information
    """
    location: str = None
    time: datetime = None
    temperature: float = None
    humidity: str = None
    wind: str = None
    weather_code: int = None


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

    raise WeatherAPIError(response_json["message"], response.status_code)


def parse_weather_data_by_location(location_input):
    """
    Parses the response json from the weather api and puts it in the weather class

    Parameters:
        location_input - location string defining for where the api should get the weather for

    Returns:
        array - array containing 4 weather objects with the forecast for the next 6 hours
    """
    try:
        data = grab_forecast_by_city(location_input)
    except WeatherAPIError as e:
        return e

    hourly = data["timelines"]["hourly"]
    location = data["location"]["name"]

    def create_weather_object(values, location, time):
        temp = values["temperature"]
        humi = values["humidity"]
        wind = values["windSpeed"]
        weather_code = values["weatherCode"]
        print(weather_code)
        return Weather(
            location=location,
            time=datetime.strftime(time, "%d.%m. %H:%M Uhr"),
            temperature=temp,
            humidity=humi,
            wind=wind,
            weather_code=weather_code)

    next_hour = create_weather_object(hourly[2]["values"], location, datetime.strptime(
        hourly[2]["time"], "%Y-%m-%dT%H:%M:%SZ"))

    two_hours = create_weather_object(hourly[4]["values"], location, datetime.strptime(
        hourly[4]["time"], "%Y-%m-%dT%H:%M:%SZ"))

    fours_hours = create_weather_object(hourly[6]["values"], location, datetime.strptime(
        hourly[6]["time"], "%Y-%m-%dT%H:%M:%SZ"))

    six_hours = create_weather_object(hourly[8]["values"], location, datetime.strptime(
        hourly[8]["time"], "%Y-%m-%dT%H:%M:%SZ"))

    return [next_hour, two_hours, fours_hours, six_hours]
