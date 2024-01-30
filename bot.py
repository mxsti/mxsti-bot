import discord
from discord.ext import commands
from reddit import get_post
from dotenv import load_dotenv
import os

# env variables
load_dotenv()
bot_token = os.environ.get("BOT_TOKEN")

# set up bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot ready as {bot.user} - ID: {bot.user.id}')

@bot.command()
async def rreddit(ctx, subredditname: str):
    """Gets random Post from given subreddit"""
    try:
        post = get_post(subredditname)
    except:
        await ctx.send("Subreddit unbekannt")     
    await ctx.send(post)


bot.run(bot_token)