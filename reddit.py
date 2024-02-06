"""os needed to grab env variables"""
import os
import random
import praw
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
        subredditname (str): Name of the subreddit
        
    Returns:
        post url(str): the URL of a random post    
    """
    posts = []
    for post in reddit.subreddit(subredditname).hot(limit=10):
        posts.append(post.url)
    return random.choice(posts)
