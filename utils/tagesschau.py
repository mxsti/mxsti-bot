""" helper functions to interact with tagesschau api """
from dataclasses import dataclass

import requests

from enum import Enum

from utils.exceptions import TagesschauAPIError


class Ressort(Enum):
    """ Enum for the different ressorts """
    INLAND = "inland"
    AUSLAND = "ausland"
    WIRTSCHAFT = "wirtschaft"
    SPORT = "sport"
    VIDEO = "video"
    INVESTIGATIV = "investigativ"
    WISSEN = "wissen"


@dataclass
class News:
    """
    Class containing news metadata
    """
    title: str = None
    detailsWeb: str = None
    breakingNews: bool = None
    teaserImageUrl: str = None


def get_news(ressort: Ressort):
    """
    Calls the tagesschau api and grabs the latest news for given ressort

    Parameters:
        ressort: ressort of the news

    Returns:
        response JSON from the tagesschau api
    """
    # 4 is the region - defaulting to brandenburg
    url = f'https://www.tagesschau.de/api2u/news/?regions=4&ressort={ressort.value}'
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers, timeout=4)
    response_json = response.json()

    if response.status_code == 200:
        return response_json

    raise TagesschauAPIError(response_json["error"], response.status_code)


def parse_news_data_by_ressort(ressort: Ressort):
    """
    Parses the response json from the tagesschau api and puts it in the news class

    Parameters:
        ressort: ressort of the news

    Returns:
        array - array containing news objects with the latest news for the given ressort
    """
    def create_news_object(news_data):
        title = news_data["title"]
        teaser_image_url =  news_data["teaserImage"]["imageVariants"]["1x1-144"]
        details_web = news_data["detailsweb"]
        breaking_news = news_data["breakingNews"]
        return News(title=title, teaserImageUrl=teaser_image_url, detailsWeb=details_web, breakingNews=breaking_news)

    try:
        data = get_news(ressort)
    except TagesschauAPIError as e:
        return e

    news = data["news"][:3]  # we only want the newest news
    parsed_news = []
    for n in news:
        parsed_news.append(create_news_object(n))

    return parsed_news
