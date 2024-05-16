""" Canyon Bike helper functions to check availability of chosen bikes  """

from dataclasses import dataclass
from typing_extensions import Literal
from bs4 import BeautifulSoup
import requests


@dataclass
class Bike():
    """
    Class containing bike data
    """
    name: str = None
    variant: Literal["3XS", "2XS", "XS", "S",
                     "M", "L", "XL", "2XL", "3XL"] = None
    url: str = None
    available: bool = False


def check_bike(name, variant, url):
    """
    Parses the canyon shop website and returns a bool if the given bike is available

    Parameters:
        name: Name of the bike
        variant: variant of the bike (XS, S, M, L ...)
        url: shop url of the bike

    Returns:
       Bike: Dataclass of the bike with availability
    """
    # grab current shop website and parse
    page = requests.get(url, timeout=1000)
    soup = BeautifulSoup(page.text, features="html.parser")

    # find buttons with the different variants
    variants = soup.find_all(class_="productConfiguration__selectVariant")
    for v in variants:
        if v.getText().strip() == variant:
            if "js-unpurchasable" in v["class"]:
                return (Bike(name=name, variant=variant,
                             url=url, available=False))
            if "productConfiguration__selectVariant--purchasable" in v["class"]:
                return (Bike(name=name, variant=variant,
                             url=url, available=True))
    return None
