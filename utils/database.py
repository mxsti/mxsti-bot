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


def addreminder_db(topic, date):
    """
    Inserts a new row into reminder table

    Parameters:
        topic: topic of what is to be reminded
        data: when to remind the user

    Returns:
        on success: 1 (int)
        on error: sqlite3.Error
    """
    try:
        cur.execute(
            f"""
        INSERT INTO reminder
        (topic, date)
        VALUES('{topic}', '{date}');
        """
        )
        con.commit()
        con.close()
        return 1
    except sqlite3.Error as e:
        print(f"Error inserting data into reminder table: {e}")
        con.close()
        return e
