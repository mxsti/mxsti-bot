""" get random stromberg quotes """

import json
import os
import random


def get_random_quote():
    """
    Returns random stromberg quote

    Returns:
        quote: string containing random quote
    """
    filepath = f"{os.getcwd()}/utils/stromberg_quotes.json"
    with open(filepath, encoding='utf-8') as f:
        quotes = json.load(f)

    return random.choice(quotes)["quote"]
