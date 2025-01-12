from os import getenv
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN")

ADMIN_IDS = int(getenv("ADMIN_ID"))

DATABASE = {
    "host": getenv("DB_HOST", "localhost"),
    "database": getenv("DB_NAME"),
    "user": getenv("DB_USER"),
    "password": getenv("DB_PASSWORD")
} 