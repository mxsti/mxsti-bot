"""os needed to grab env variables"""
import os
import random
import praw
from praw.models.listing.generator import ListingGenerator
# get env variables
from dotenv import load_dotenv
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
    posts: ListingGenerator = reddit.subreddit(subredditname).hot(limit=10)
    if posts.yielded == 0:
        raise SubredditNotFoundOrEmptyError(subredditname)

    posts_urls = []
    for post in posts:
        posts_urls.append(post.url)

    return random.choice(posts_urls)

class SubredditNotFoundOrEmptyError(Exception):
    """
    Custom Exception when a Subreddit is empty or it does not exist
    
    Attributes:
        subredditname: name of the not existing subreddit
        message: explanation of the error
    """
    def __init__(self, subredditname, message="Subreddit not found or empty"):
        self.subredditname = subredditname
        self.message = message
        super().__init__(self.message)
