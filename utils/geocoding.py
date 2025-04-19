""" helper functions to resolve addresses and geolocations """

import os
from dataclasses import dataclass
import requests
from dotenv import load_dotenv
from utils.exceptions import APIError

load_dotenv()
API_KEY = os.environ.get("GEOCODE_API_KEY")


@dataclass
class Geolocation:
    """
    Class containing Geolocation and address
    """
    address: str = None
    lat: str = None
    lng: str = None


def resolve_address(address: str):
    """
    Calls the geocoding api and resolves the address to latlng

    Returns:
        lat lng object
    """
    url = f'https://geocode.maps.co/search?q={address}&api_key={API_KEY}'  # pylint: disable=duplicate-code
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers, timeout=4)
    response_json = response.json()

    if response.status_code == 200:
        return Geolocation(
            address=address,
            lat=response_json[0]["lat"], lng
            =response_json[0]["lon"])

    raise APIError(response_json["message"], response.status_code)
