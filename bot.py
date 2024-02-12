""" discord bot file defining the setup and all commands/tasks of the bot """

import os
import logging
from sqlite3 import Error
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.reddit import get_post, SubredditNotFoundOrEmptyError
from utils.database import addreminder_db

# env variables
load_dotenv()
bot_token = os.environ.get("BOT_TOKEN")

# set up logging
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='a')

# set up bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)


@bot.event
async def on_ready():
    """
    Logs when the bot has started successfully
    """
    print(f'Bot ready as {bot.user} - ID: {bot.user.id}')


##########
# REDDIT #
##########
@bot.command()
async def rreddit(ctx, subredditname: str):
    """
    User command - Posts a random post from given subreddit

    Parameters:
        ctx: Context of the Command (User, Channel ...)
        subredditname (str): Name of the subreddit

    Returns:
        nothing - posts in the channel the command was posted
    """
    try:
        post = get_post(subredditname)
        await ctx.send(post)
    except SubredditNotFoundOrEmptyError as e:
        print(f"Error grabbing posts: {e.subredditname} - {e.message}")
        await ctx.send(f"Subreddit {subredditname} unbekannt!")


############
# REMINDER #
############
@bot.command()
async def addreminder(ctx, topic, date):
    """
    User command - Adds a new reminder to the db

    Parameters:
        ctx: Context of the Command (User, Channel ...)
        topic: topic of the reminder (e.g. Birthday Frank)
        date: when to remind the user (Format: )

    Returns:
        nothing - posts in the channel the command was posted (success or error)
    """
    resp = addreminder_db(topic, date)
    if isinstance(resp, Error):  # sqlite Error
        await ctx.send("Das hat nicht geklappt :(")
    else:
        await ctx.send(f"{topic} erfolgreich eingefügt")


# start the bot
bot.run(bot_token, log_handler=handler)
