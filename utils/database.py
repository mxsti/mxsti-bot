"""" helper to connect and work with the sqlite3 database """

import os
import sqlite3
from dotenv import load_dotenv

# env variables
load_dotenv()
db_path = os.environ.get("DATABASE")

# set up db connection
con = sqlite3.connect(db_path)
cur = con.cursor()


def addreminder_db(topic, date, channel):
    """
    Inserts a new row into reminder table

    Parameters:
        topic: topic of what is to be reminded
        date: when to remind the user
        channel: the channel where the command was posted

    Returns:
        on success: 1 (int)
        on error: sqlite3.Error
    """
    try:
        cur.execute(
            f"""
        INSERT INTO reminder
        (topic, date, channel_id)
        VALUES('{topic}', '{date}', '{channel}');
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
