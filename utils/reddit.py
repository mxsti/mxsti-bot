""" reddit helper functions to interact with reddit api via praw"""

import os
import random
import praw
from praw.models import Subreddit
from dotenv import load_dotenv
from utils.exceptions import SubredditNotFoundOrEmptyError

load_dotenv()

CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
USER_AGENT = os.environ.get("REDDIT_USER_AGENT")

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)


def get_post(subredditname):
    """
    Returns random hot post from given subreddit using the reddit api

    Parameters:
        subredditname: Name of the subreddit

    Returns:
        post url: the URL of a random post    
    """
    subreddit: Subreddit = reddit.subreddit(subredditname)
    posts = []
    try:
        for post in subreddit.hot(limit=10):
            posts.append(post.url)
    except Exception as e:
        raise SubredditNotFoundOrEmptyError(subredditname) from e

    return random.choice(posts)
