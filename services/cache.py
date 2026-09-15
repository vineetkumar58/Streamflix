import json

import redis

from config import Config


redis_client = redis.Redis(

    host=Config.REDIS_HOST,

    port=Config.REDIS_PORT,

    decode_responses=True

)


def get_cache(key):

    try:

        value = redis_client.get(key)

        if value is None:

            return None

        return json.loads(value)

    except Exception as error:

        print(
            "Redis GET error:",
            error
        )

        return None


def set_cache(
    key,
    value,
    expiration=60
):

    try:

        redis_client.setex(

            key,

            expiration,

            json.dumps(value)

        )

        return True

    except Exception as error:

        print(
            "Redis SET error:",
            error
        )

        return False


def delete_cache(key):

    try:

        redis_client.delete(key)

        return True

    except Exception as error:

        print(
            "Redis DELETE error:",
            error
        )

        return False
