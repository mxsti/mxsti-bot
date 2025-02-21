""" helper to connect and work with the sqlite3 database for the reminders """

import os
import sqlite3
from dotenv import load_dotenv

# env variables
# pylint: disable=duplicate-code
load_dotenv()
db_path = os.environ.get("DATABASE")

# set up db connection
con = sqlite3.connect(db_path)
cur = con.cursor()


def addreminder_db(topic, date, channel, sender):
    """
    Inserts a new row into reminder table

    Parameters:
        topic: topic of what is to be reminded
        date: when to remind the user
        channel: the channel where the command was posted
        sender: the user who send the reminder

    Returns:
        on success: 1 (int)
        on error: sqlite3.Error
    """
    try:
        cur.execute(
            f"""
        INSERT INTO reminder
        (topic, date, channel_id, sender)
        VALUES('{topic}', '{date}', '{channel}', '{sender}');
        """
        )
        con.commit()
        return 1
    except sqlite3.Error as e:
        return e  # return back to caller, logging is handled there


def fetch_reminders():
    """
    Fetches all reminders from the database

    Returns:
        array of reminders
    """
    try:
        resp = cur.execute("SELECT * FROM reminder;")
        reminders = resp.fetchall()
        return reminders
    except sqlite3.Error as e:
        return e  # return back to caller, logging is handled there


def delete_reminder(topic, date, channel, sender):
    """
    Deletes given reminder from database
    Parameters:
        topic: topic of reminder
        date: date of reminder
        channel: channel reminder was posted in

    Returns:
        True or sqlite Error
    """
    try:
        cur.execute(
            f"DELETE FROM reminder WHERE"
            f"(topic = '{topic}')"
            f"AND (date = '{date}')"
            f"AND (channel_id = {channel})"
            f"AND (sender = {sender});"
        )
        con.commit()
        return True
    except sqlite3.Error as e:
        return e  # return back to caller, logging is handled there
