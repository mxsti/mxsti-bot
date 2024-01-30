import praw
import random
# get env variables
from dotenv import load_dotenv
load_dotenv()
import os

client_id = os.environ.get("REDDIT_CLIENT_ID")
client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
user_agent = "macos:discordbot:1.0 (by u/Impossible-Gain-4097)"

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)

def get_post(subredditname):
    posts = []
    for post in reddit.subreddit(subredditname).hot(limit=10):
        posts.append(post.url)
    return random.choice(posts)