""" helper functions to grab current fuel prices """

import os
from dataclasses import dataclass
import requests
from dotenv import load_dotenv
from utils.geocoding import resolve_address
from utils.exceptions import APIError

load_dotenv()
API_KEY = os.environ.get("FUEL_API_KEY")


@dataclass
class Station:
    """
    Class containing station info with prices
    """
    brand: str
    name: str
    is_open: bool
    diesel: float
    e5: float
    e10: float


def get_station_prices_by_address(address: str):
    """
    Calls the fuel api and and gets prices for address with radius 20km

    Returns:
        station array
    """
    stations_with_prices = []
    latlng = resolve_address(address)
    api_base_url = "https://creativecommons.tankerkoenig.de/json/list.php"
    url = (f'{api_base_url}'
           f'?lat={latlng.lat}'
           f'&lng={latlng.lng}'
           f'&rad=20&sort=dist'
           f'&type=all'
           f'&apikey={API_KEY}')
    headers = {"accept": "application/json"}  # pylint: disable=duplicate-code
    response = requests.get(url, headers=headers, timeout=4)
    response_json = response.json()

    if response.status_code == 200:
        stations = response_json["stations"]
        for station in stations:
            stations_with_prices.append(Station(
                brand=station["brand"],
                name=station["name"],
                is_open=station["isOpen"],
                diesel=station["diesel"],
                e5=station["e5"],
                e10=station["e10"]
            ))
        return stations_with_prices

    raise APIError(response_json["message"], response.status_code)
