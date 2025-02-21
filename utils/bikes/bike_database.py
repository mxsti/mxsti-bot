""" helper to connect and work with the sqlite3 database for the bike utility """

import os
import sqlite3
from dotenv import load_dotenv

# env variables
load_dotenv()
# pylint: disable=duplicate-code
db_path = os.environ.get("DATABASE")

# set up db connection
con = sqlite3.connect(db_path)
cur = con.cursor()


def add_bike(name, variant, url, channel, sender):
    """
    Inserts a new row into bike table

    Parameters:
        name: name of the bike
        variant: variant of the bike (3XS - 2XL)
        url: url canyon shop url of the bike
        channel: the channel where the command was posted
        sender: the user who send the command

    Returns:
        on success: 1 (int)
        on error: sqlite3.Error
    """
    try:
        cur.execute(
            f"""
        INSERT INTO bike
        (name, variant, url, channel_id, sender)
        VALUES('{name}', '{variant}', '{url}', '{channel}', '{sender}');
        """
        )
        con.commit()
        return 1
    except sqlite3.Error as e:
        print(e)
        return e  # return back to caller, logging is handled there


def fetch_bikes():
    """
    Fetches all bikes from the database which are not muted

    Returns:
        array of bikes
    """
    try:
        resp = cur.execute("SELECT * FROM bike where muted=false;")
        bikes = resp.fetchall()
        return bikes
    except sqlite3.Error as e:
        return e  # return back to caller, logging is handled there


def delete_bike(name, variant, channel, sender):
    """
    Deletes given bike from database
    Parameters:
        name: name of the bike which should be deleted
        variant: variant of the bike
        channel: channel reminder was posted in
        sender: user who added the bike

    Returns:
        True or sqlite Error
    """
    try:
        cur.execute(
            f"DELETE FROM bike WHERE"
            f"(name = '{name}')"
            f"AND (variant = '{variant}')"
            f"AND (channel_id = {channel})"
            f"AND (sender = {sender});"
        )
        con.commit()
        return True
    except sqlite3.Error as e:
        return e  # return back to caller, logging is handled there


def mute_bike(name, variant, channel, sender):
    """
    Sets mute column to true for given bike
    Parameters:
    name: name of the bike which should be deleted
    variant: variant of the bike
    channel: channel reminder was posted in
    sender: user who added the bike

    Returns:
        True or sqlite Error
    """
    try:
        cur.execute(
            f"UPDATE bike set muted=true WHERE"
            f"(name = '{name}')"
            f"AND (variant = '{variant}')"
            f"AND (channel_id = {channel})"
            f"AND (sender = {sender});"
        )
        con.commit()
        return True
    except sqlite3.Error as e:
        return e  # return back to caller, logging is handled there


def unmute_bike(name, variant, channel, sender):
    """
    Sets mute column to false for given bike
    Parameters:
    name: name of the bike which should be deleted
    variant: variant of the bike
    channel: channel reminder was posted in
    sender: user who added the bike

    Returns:
        True or sqlite Error
    """
    try:
        cur.execute(
            f"UPDATE bike set muted=false WHERE"
            f"(name = '{name}')"
            f"AND (variant = '{variant}')"
            f"AND (channel_id = {channel})"
            f"AND (sender = {sender});"
        )
        con.commit()
        return True
    except sqlite3.Error as e:
        return e  # return back to caller, logging is handled there
