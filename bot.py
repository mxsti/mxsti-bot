""" discord bot file defining the setup and all commands/tasks of the bot """

from datetime import datetime
import os
import logging
import sqlite3
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from utils.reddit import get_post
from utils.database import addreminder_db, fetch_reminders, delete_reminder, add_bike, fetch_bikes
from utils.weather_api import (
    parse_weather_data_by_location_today, parse_weather_data_by_location_tomorrow)
from utils.exceptions import WeatherAPIError, SubredditNotFoundOrEmptyError
from utils.canyon_bikes import check_bike

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
    loop_check_reminders.start()
    loop_check_bikes.start()


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
async def remindme(ctx, topic, date):
    """
    User command - Adds a new reminder to the db

    Parameters:
        ctx: Context of the Command (User, Channel ...)
        topic: topic of the reminder (e.g. Birthday Frank)
        date: when to remind the user (Format: )

    Returns:
        nothing - posts in the channel the command was posted (success or error)
    """
    # check if reminder is for today or another day
    if len(date.split(" ")) == 1:
        today_day = datetime.now().day
        today_month = datetime.now().month
        date = f"{today_day}.{today_month}. {date}"
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

    resp = addreminder_db(topic, parsed_date,
                          ctx.channel.id, ctx.message.author.id)

    if isinstance(resp, sqlite3.Error):  # sqlite Error
        logger.error("User: %s - Command: %s - Error: %s",
                     ctx.author, ctx.command, resp)
        await ctx.send("Das hat nicht geklappt")
    else:
        await ctx.message.add_reaction('👍🏻')


@tasks.loop(seconds=10.0)
async def loop_check_reminders():
    """
    Task - Checks all reminders if there is something to remind now
    Runs every 20 seconds

    Returns:
        nothing - posts in the channel if there is a reminder now
    """
    reminders = fetch_reminders()

    now = datetime.now().replace(microsecond=0).replace(second=0)

    for reminder in reminders:
        topic = reminder[0]
        date = reminder[1]
        channel_id = reminder[2]
        sender = reminder[3]

        time_to_remind = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        if time_to_remind == now:
            channel = bot.get_channel(channel_id)
            embed_title = "Erinnerung"
            embed_desc = f"<@{sender}>\n{topic}"
            embed_color = discord.Color.random()
            embed = discord.Embed(
                title=embed_title, description=embed_desc, color=embed_color)
            # create funny avatar for user
            embed.set_thumbnail(url=f'https://robohash.org/{sender}')
            await channel.send(embed=embed)
            resp = delete_reminder(
                topic, date, channel_id, sender)
            if isinstance(resp, sqlite3.Error):  # sqlite Error
                logger.error("Task: check_reminders - Error: %s",
                             resp)


###########
# WEATHER #
###########
@bot.command()
async def weather(ctx, location):
    """
    User command - Gets the weather for the location

    Parameters:
        ctx: Context of the Command (User, Channel ...)
        location: location where the forecast is for

    Returns:
        nothing - posts in the channel the command was posted (success or error)
    """

    # get the weather objects
    weather_forecast = parse_weather_data_by_location_today(location)
    if isinstance(weather_forecast, WeatherAPIError):
        logger.error("User: %s - Command: %s - Error: %s",
                     ctx.author, ctx.command, weather_forecast)
        await ctx.send(f"Ort {location} nicht gefunden")
        return

    # build the embed
    weather_code = weather_forecast[0].metadata.weather_code
    icon = discord.File(
        f"utils/weather_icons/{weather_code}.png", filename=f"{weather_code}.png")
    embed_title = f"Wetter Vorhersage für {weather_forecast[0].metadata.location}"
    embed_color = discord.Color.random()
    embed = discord.Embed(
        title=embed_title, color=embed_color)
    embed.set_thumbnail(url=f"attachment://{weather_code}.png")
    for forecast in weather_forecast:
        embed.add_field(
            name=forecast.metadata.time,
            value=f"""
                {forecast.temperature} °C
                {forecast.wind} km/h Wind
                {forecast.humidity}% Feuchtigkeit""")

    await ctx.send(file=icon, embed=embed)


@bot.command()
async def weathertm(ctx, location):
    """
    User command - Gets the weather for the location

    Parameters:
        ctx: Context of the Command (User, Channel ...)
        location: location where the forecast is for

    Returns:
        nothing - posts in the channel the command was posted (success or error)
    """

    # get the weather objects
    weather_forecast = parse_weather_data_by_location_tomorrow(location)
    if isinstance(weather_forecast, WeatherAPIError):
        logger.error("User: %s - Command: %s - Error: %s",
                     ctx.author, ctx.command, weather_forecast)
        await ctx.send(f"Ort {location} nicht gefunden")
        return

    # build the embed
    weather_code = weather_forecast.metadata.weather_code
    icon = discord.File(
        f"utils/weather_icons/{weather_code}.png", filename=f"{weather_code}.png")
    embed_title = f"Wetter Vorhersage für {weather_forecast.metadata.location}"
    embed_color = discord.Color.random()
    embed = discord.Embed(
        title=embed_title, color=embed_color)
    embed.set_thumbnail(url=f"attachment://{weather_code}.png")
    embed.add_field(
        name=weather_forecast.metadata.time,
        value=f"""
            {weather_forecast.temperature_avg} °C Durchschnitt
            {weather_forecast.temperature_max} °C Max
            {weather_forecast.temperature_min} °C Min
            {weather_forecast.sunrise_time} Sonnenaufgang
            {weather_forecast.sunset_time} Sonnenuntergang""")

    await ctx.send(file=icon, embed=embed)


#################
# CANYON BIKES  #
################


@bot.command()
async def addbike(ctx, name, variant, url):
    """
    User command - Adds a new bike I want to be reminded of to the db

    Parameters:
        ctx: Context of the Command (User, Channel ...)
        name: name of the bike (e.g. Canyon Endurace AL6)
        variant: variant of the bike (3XS - 2XL)
        url: url of the bike in the shop 

    Returns:
        nothing - posts in the channel the command was posted (success or error)
    """

    resp = add_bike(name, variant, url,
                    ctx.channel.id, ctx.message.author.id)

    if isinstance(resp, sqlite3.Error):  # sqlite Error
        logger.error("User: %s - Command: %s - Error: %s",
                     ctx.author, ctx.command, resp)
        await ctx.send("Das hat nicht geklappt")
    else:
        await ctx.message.add_reaction('👍🏻')


@tasks.loop(seconds=10.0)
async def loop_check_bikes():
    """
    Task - Checks all bikes and send a message if a bike is available
    Runs every 30 minutes

    Returns:
        nothing - posts in the channel if there is a available bike
    """
    bikes = fetch_bikes()

    for bike in bikes:
        bike_with_availability = check_bike(
            name=bike[0], variant=bike[1], url=bike[2])

        if bike_with_availability.available:
            channel = bot.get_channel(bike[3])
            embed_title = "Bike verfügbar!"
            embed_desc = f"""
                        Hey < @{bike[4]} >,
                        das Bike {bike[0]} in {bike[1]} ist jetzt verfügbar!\n{bike[2]}"""
            embed_color = discord.Color.random()
            embed = discord.Embed(
                title=embed_title, description=embed_desc, color=embed_color)
            await channel.send(embed=embed)


# start the bot
bot.run(bot_token, log_handler=handler)
