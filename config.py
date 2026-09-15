import os

from dotenv import load_dotenv


load_dotenv()


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "streamflix-development-secret"
    )


    DB_HOST = os.getenv(
        "DB_HOST",
        "localhost"
    )


    DB_PORT = int(
        os.getenv(
            "DB_PORT",
            "3306"
        )
    )


    DB_USER = os.getenv(
        "DB_USER",
        "streamflix"
    )


    DB_PASSWORD = os.getenv(
        "DB_PASSWORD",
        "streamflix_password"
    )


    DB_NAME = os.getenv(
        "DB_NAME",
        "streamflix"
    )


    REDIS_HOST = os.getenv(
        "REDIS_HOST",
        "localhost"
    )


    REDIS_PORT = int(
        os.getenv(
            "REDIS_PORT",
            "6379"
        )
    )
