import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():

    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "streamflix"),
        password=os.getenv("DB_PASSWORD", "streamflix_password"),
        database=os.getenv("DB_NAME", "streamflix")
    )
