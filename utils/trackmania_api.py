""" Helper functions to communicate with the Nadeo/Trackmania API """

import os
import json
import requests
from dotenv import load_dotenv
from utils.exceptions import TrackmaniaAPIError

# env variables
load_dotenv()

BASIC_TOKEN = os.environ.get("TRACKMANIA_BASIC_AUTH")
USER_AGENT = os.environ.get("TRACKMANIA_USER_AGENT")


def _auth1():
    """ 
    Auth @ Nadeo API is split into two parts more info 
    here (https://webservices.openplanet.dev/auth)
    This is the first step

    Returns:
        ticket to authenticate in the next step
    """

    url = "https://public-ubiservices.ubi.com/v3/profiles/sessions"
    headers = {
        "Content-Type": "application/json",
        "Ubi-AppId": "86263886-327a-4328-ac69-527f0d20a237",
        "User-Agent": USER_AGENT,
        "Authorization": f"Basic {BASIC_TOKEN}"
    }

    response = requests.request(
        "POST", url, headers=headers, timeout=4)
    response_json = response.json()

    if response.status_code == 200:
        return response_json["ticket"]

    raise TrackmaniaAPIError(
        response_json["message"], response.status_code)


def _auth2(ticket):
    """ 
    Auth @ Nadeo API is split into two parts more info 
    here (https://webservices.openplanet.dev/auth)
    This is the second step

    Parameters:
        ticket: auth token from the first step

    Returns:
        final access token to authenticate @ nadeo live service
    """

    url = "https://prod.trackmania.core.nadeo.online/v2/authentication/token/ubiservices"

    payload = json.dumps({"audience": "NadeoLiveServices"})

    headers = {
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
        "Authorization": f"ubi_v1 t={ticket}"
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, timeout=4)
    response_json = response.json()

    if response.status_code == 200:
        return response_json["accessToken"]

    raise TrackmaniaAPIError(
        response_json["message"], response.status_code)


def fetch_trophy_points(account_id):
    """
    gets the trophy points for a player from the trackmania nadeo live services
    api documentation here: https://webservices.openplanet.dev/live/leaderboards/trophies

    Parameters:
        account_id: account_id to identify the player

    Returns:
        json object, containing total trophy points and ranking for every player  
    """

    # authenticate
    # TODO
    # implement clean refresh token workflow,
    # so we don't have todo the whole auth process every time
    try:
        step1_ticket = _auth1()
        access_token = _auth2(step1_ticket)
    except TrackmaniaAPIError as e:
        return e

    url = "https://live-services.trackmania.nadeo.live/api/token/leaderboard/trophy/player"
    payload = json.dumps({"listPlayer": [{"accountId": account_id}]})

    headers = {
        "Authorization": f"nadeo_v1 t={access_token}"
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, timeout=4)

    if response.status_code != 200:
        raise TrackmaniaAPIError(
            "something went wrong", response.status_code)

    # parse data
    response_json_rankings = response.json()["rankings"][0]
    trophy_points = response_json_rankings["countPoint"]
    zone_rankings_json = response_json_rankings["zones"]
    zone_rankings = []
    for zone in zone_rankings_json:
        zone_name = zone["zoneName"]
        rank = zone["ranking"]["position"]
        zone_rankings.append(
            {
                "zone_name": zone_name,
                "rank": rank,
            })

    return TrackmaniaTrophyRanking(trophy_points, zone_rankings)


class TrackmaniaTrophyRanking():
    """
    Class defining Trackmania trophy ranking for a player

    Attributes:
        message: http error message
        code: http error code
    """

    def __init__(self, trophy_points, zone_rankings):
        self.trophy_points = trophy_points
        self.zone_rankings = zone_rankings
