import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN n'est pas configuré.")

MIN_DEPOSIT = 25.00

BOT_NAME = "YOHAN PREDICTION BOT"
