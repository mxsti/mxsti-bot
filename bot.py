""" os needed to grab env variables """
import os
import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandInvokeError
from dotenv import load_dotenv
from reddit import get_post

# env variables
load_dotenv()
bot_token = os.environ.get("BOT_TOKEN")

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

@bot.command()
async def rreddit(ctx, subredditname: str):
    """
    User command - Posts a random post from given subreddit
    
    Parameters:
        ctx (any): Context of the Command (User, Channel ...)
        subredditname (str): Name of the subreddit
        
    Returns:
        nothing - posts in the channel the command was posted
    """
    try:
        post = get_post(subredditname)
    except:
        await ctx.send("Subreddit unbekannt!")
    await ctx.send(post)

# start the bot
bot.run(bot_token)
