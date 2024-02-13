""" discord bot file defining the setup and all commands/tasks of the bot """

from datetime import datetime
import os
import logging
from sqlite3 import Error
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from utils.reddit import get_post, SubredditNotFoundOrEmptyError
from utils.database import addreminder_db, fetch_reminders, delete_reminder

# env variables
load_dotenv()
bot_token = os.environ.get("BOT_TOKEN")

# set up logging
logger = logging.getLogger("discord")
formatter = logging.Formatter(
    '[{asctime}] [{levelname:<8}] {name}: {message}', '%d.%m.%Y %H:%M:%S', style='{')
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='a')
handler.setFormatter(formatter)
logger.addHandler(handler)

# set up bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)


@bot.event
async def on_ready():
    """
    Logs when the bot has started successfully
    Starts all tasks when bot is ready
    """
    logger.info("Bot ready as %s - ID: %s", bot.user, bot.user.id)
    check_reminders.start()


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
        logger.error("User: %s - Command: %s - Error: %s",
                     ctx.author, ctx.command, e)
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
    # parse datetime
    try:
        parsed_date = datetime.strptime(
            date, "%d.%m. %H:%M").replace(year=datetime.today().year)
    except ValueError as e:
        logger.error("User: %s - Command: %s - Error: %s",
                     ctx.author, ctx.command, e)
        await ctx.send(f"{date} ist nicht im korrekten Format (Tag.Monat. Stunde:Minute) "
                       f"- Datum und Beschreibung müssen in Anführungszeichen sein")
        return

    resp = addreminder_db(topic, parsed_date, ctx.channel.id)

    if isinstance(resp, Error):  # sqlite Error
        logger.error("User: %s - Command: %s - Error: %s",
                     ctx.author, ctx.command, Error)
        await ctx.send("Das hat nicht geklappt")
    else:
        await ctx.message.add_reaction('👍🏻')


@tasks.loop(seconds=10.0)
async def check_reminders():
    """
    Task - Checks all reminders if there is something to remind now
    Runs every 20 seconds

    Returns:
        nothing - posts in the channel if there is a reminder now
    """
    reminders = fetch_reminders()

    now = datetime.now().replace(microsecond=0).replace(second=0)

    for reminder in reminders:
        time_to_remind = datetime.strptime(reminder[1], "%Y-%m-%d %H:%M:%S")
        if time_to_remind == now:
            channel = bot.get_channel(reminder[2])
            embed = discord.Embed(title="Erinnerung",
                                  description=reminder[0], color=discord.Colour.random())
            await channel.send(embed=embed)
            resp = delete_reminder(reminder[0], reminder[1], reminder[2])
            if isinstance(resp, Error):  # sqlite Error
                logger.error("Task: check_reminders - Error: %s", resp)


# start the bot
bot.run(bot_token, log_handler=handler)
