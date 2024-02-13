"""" file to init the database used by the bot """

import os
import sqlite3
from dotenv import load_dotenv

# env variables
load_dotenv()
db_path = os.environ.get("DATABASE")

# set up db connection
con = sqlite3.connect(db_path)
cur = con.cursor()

# reminder table
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS reminder (
        topic TEXT NOT NULL,
        date TEXT NOT NULL,
        channel_id INTEGER NOT NULL
    );
    """
)
