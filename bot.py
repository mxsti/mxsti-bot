""" discord bot file defining the setup and all commands/tasks of the bot """

from datetime import datetime
import os
import logging
import shutil
import sqlite3
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from utils.bikes.bike_helper import check_bike
from utils.news.tagesschau_helper import (
    Ressort, parse_news_data_by_ressort, News, get_tagesschau_video_url)
from utils.news.news_exception import TagesschauAPIError
from utils.weather.weather_api_helper import (
    parse_weather_data_by_location_today, parse_weather_data_by_location_tomorrow)
from utils.weather.weather_exception import WeatherAPIError
from utils.reddit.reddit_helper import get_post
from utils.reddit.reddit_exception import SubredditNotFoundOrEmptyError
from utils.reminder.reminder_database import addreminder_db, fetch_reminders, delete_reminder
from utils.bikes.bike_database import delete_bike, add_bike, fetch_bikes, mute_bike, unmute_bike
from utils.stromberg.stromberg_helper import get_random_quote
from utils.youtubedl.y2ubedownload_helper import download_audio
from utils.youtubedl.y2ubedownloader_exception import DownloadFailedError

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
    loop_clear_audio.start()
    # loop_check_bikes.start()


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
        f"utils/weather/weather_icons/{weather_code}.png", filename=f"{weather_code}.png")
    embed_title = f"Wetter Vorhersage für {
        weather_forecast[0].metadata.location}"
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
        await ctx.message.add_reaction("👍🏻")


@bot.command()
async def removebike(ctx, name, variant):
    """
    User command - removes a bike from the db

    Parameters:
        ctx: Context of the Command (User, Channel ...)
        name: name of the bike (e.g. Canyon Endurace AL6)
        variant: variant of the bike (3XS - 2XL)

    Returns:
        nothing - posts in the channel the command was posted (success or error)
    """
    resp = delete_bike(
        name, variant, ctx.channel.id, ctx.message.author.id)
    if isinstance(resp, sqlite3.Error):  # sqlite Error
        logger.error("User: %s - Command: %s - Error: %s",
                     ctx.author, ctx.command, resp)
        await ctx.send("Bike konnte nicht gelöscht werden :(")
    else:
        await ctx.message.add_reaction("👍🏻")


@bot.command()
async def mutebike(ctx, name, variant):
    """
    User command - mutes a bike (still in db but not checked anymore)

    Parameters
        ctx: Context of the Command (User, Channel ...)
        name: name of the bike (e.g. Canyon Endurace AL6)
        variant: variant of the bike (3XS - 2XL)

    Returns:
        nothing - posts in the channel the command was posted (success or error)
    """
    resp = mute_bike(name, variant, ctx.channel.id, ctx.message.author.id)
    if isinstance(resp, sqlite3.Error):
        logger.error("User: %s - Command: %s - Error: %s",
                     ctx.author, ctx.command, resp)
        await ctx.send("Bike konnte nicht gemuted werden.")
    else:
        await ctx.message.add_reaction("👍🏻")


@bot.command()
async def unmutebike(ctx, name, variant):
    """
    User command - unmutes a bike (still in db but not checked anymore)

    Parameters
        ctx: Context of the Command (User, Channel ...)
        name: name of the bike (e.g. Canyon Endurace AL6)
        variant: variant of the bike (3XS - 2XL)

    Returns:
        nothing - posts in the channel the command was posted (success or error)
    """
    resp = unmute_bike(name, variant, ctx.channel.id, ctx.message.author.id)
    if isinstance(resp, sqlite3.Error):
        logger.error("User: %s - Command: %s - Error: %s",
                     ctx.author, ctx.command, resp)
        await ctx.send("Bike konnte nicht gefunden werden.")
    else:
        await ctx.message.add_reaction("👍🏻")


@tasks.loop(minutes=30)
async def loop_check_bikes():
    """
    Task - Checks all bikes and send a message if a bike is available
    Runs every 30 minutes

    Returns:
        nothing - posts in the channel if there is a available bike
    """
    bikes = fetch_bikes()
    if isinstance(bikes, sqlite3.Error):
        logger.error("Task: loop_check_bikes - Error: %s",
                     bikes)
        return
    for bike in bikes:
        bike_with_availability = check_bike(
            name=bike[0], variant=bike[1], url=bike[2])

        if bike_with_availability.available:
            channel = bot.get_channel(bike[3])
            embed_title = "Bike verfügbar!"
            embed_desc = f"""
                        Hey <@{bike[4]}>
                        das Bike {bike[0]} in {bike[1]} ist jetzt verfügbar!\n{bike[2]}"""
            embed_color = discord.Color.random()
            embed = discord.Embed(
                title=embed_title, description=embed_desc, color=embed_color)
            await channel.send(embed=embed)


#############
# STROMBERG #
#############
@bot.command()
async def stromberg(ctx):
    """
    User command - gets a random stromberg quote

    Parameters
        ctx: Context of the Command (User, Channel ...)

    Returns:
        nothing - posts in the channel the command was posted (success or error)
    """
    quote = get_random_quote()
    await ctx.send(quote)


################
# AUDIO STREAM #
################
@bot.command()
async def listen(ctx, url):
    """
    User command - play YouTube video in given audio channel

    Parameters
        ctx: Context of the Command (User, Channel ...)
        url: url of the video that should be played

    Returns:
        nothing - plays audio or sends a error message
    """
    # get voice channel of sender
    voice = ctx.message.author.voice
    if voice is None:
        await ctx.send('Du musst in einem Voice Channel sein!')
        return

    # check if bot is already connected to voice channel and switch channels
    for voice_client in bot.voice_clients:
        await voice_client.disconnect(force=True)

    await ctx.message.add_reaction('🎵')

    # download audio
    try:
        video_info = await download_audio(url)  # also downloads audio
    except DownloadFailedError as e:
        logger.error("Command: listen - Error: %s",
                     e.message)
        await ctx.send("Etwas ist schiefgelaufen, ist die URL korrekt?")
        return

    title = video_info[1]
    video_id = video_info[0]

    vc = await voice.channel.connect()

    # play audio
    vc.play(discord.FFmpegPCMAudio(
        source=f"{os.getcwd()}/audio/{title} [{video_id}].m4a"))


@bot.command()
async def stop(ctx):
    """
    User command - stops currently playing audio

    Parameters
        ctx: Context of the Command (User, Channel ...)

    Returns:
        nothing - stops audio
    """
    await ctx.message.add_reaction('👍🏻')
    # normally should only be one be bot returns a list (idk)
    for voice_client in bot.voice_clients:
        await voice_client.disconnect(force=True) # disconnect because stop doesnt work anymore


@tasks.loop(minutes=10)
async def loop_clear_audio():
    """
    Task - Clears audio folder to keep things clean and small
    Runs every 10 minutes

    Returns:
        nothing - logs if ran
    """
    shutil.rmtree(
        f"{os.getcwd()}/audio")  # currently playing audio file is not deleted
    logger.info("Task: loop_clear_audio - INFO: %s",
                "cleared audio folder")


##############
# TAGESSCHAU #
##############
@bot.command()
async def news(ctx, ressort: str):
    """
    User command - gets the latest news from the given ressort

    Parameters
        ctx: Context of the Command (User, Channel ...)
        ressort: ressort of the news

    Returns:
        nothing - posts in the channel the command was posted (success or error)
    """
    current_news: [News] = parse_news_data_by_ressort(Ressort(ressort.lower()))
    if isinstance(current_news, TagesschauAPIError):
        logger.error("User: %s - Command: %s - Error: %s",
                     ctx.author, ctx.command, current_news)
        await ctx.send("Etwas ist schiefgelaufen :(")
        return

    for n in current_news:
        embed_title = n.title
        embed_color = discord.Color.random()
        embed_desc = n.details_web
        embed = discord.Embed(
            title=embed_title, color=embed_color, description=embed_desc)
        embed.set_thumbnail(url=n.teaser_image_url)
        await ctx.send(embed=embed)

    return

@news.error
async def news_error(ctx, error):
    """
    Error handler for news command
    """
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            'Bitte gib einen Ressort an! '
            '(Sport, Wissen, Inland, Ausland, Investigativ, Wirtschaft, Video)')

    if isinstance(error, commands.CommandInvokeError):
        await (ctx.send(
            'Etwas ist schiefgelaufen, hast du das richtige Ressort angegeben?'
            ' (Sport, Wissen, Inland, Ausland, Investigativ, Wirtschaft, Video)'))


@bot.command()
async def tagesschau(ctx):
    """
    User command - gets the latest tagesschau video (20:00 Version)

    Parameters
        ctx: Context of the Command (User, Channel ...)

    Returns:
        nothing - posts in the channel the command was posted (success or error)
    """
    video_url = get_tagesschau_video_url()
    if isinstance(video_url, TagesschauAPIError):
        logger.error("User: %s - Command: %s - Error: %s",
                     ctx.author, ctx.command, video_url)
        await ctx.send("Etwas ist schiefgelaufen :(")
        return

    await ctx.message.add_reaction('📰')
    await ctx.send(video_url)

#########################################
# START BOT (LAST LINE IN FILE PLS LOL) #
########################################
bot.run(bot_token, log_handler=handler)
