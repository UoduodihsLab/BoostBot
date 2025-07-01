import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TORTOISE_ORM = {
    "connections": {"default": "asyncpg://postgres:Wdnmd1314159...@127.0.0.1:5432/boosterbotpro"},
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

DB_URL = 'asyncpg://postgres:Wdnmd1314159...@127.0.0.1:5432/boosterbotpro'
TORTOISE_MODULES = {'models': ['models']}

DB_CONNECTIONS_MAX = 10
DB_CONNECTIONS_MIN = 2
DB_TIMEOUT = 10
DB_POOL_RECYCLE = 3600

BOT_TOKEN = '7206853820:AAGDpvJskONRyU2JNjHYuDUhdTrNvDxKa1Q'
API_ID = 23465334
API_HASH = '0d70f50f150b9fe7380f537c08250195'
