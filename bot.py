import os

from telegram.ext import (
    Application,
    CommandHandler,
)

from database import init_db
from handlers.menu import start
from handlers.games import register_game_handlers
from handlers.verification import register_verification_handlers


TOKEN = os.getenv("TELEGRAM_TOKEN")


def main():

    if not TOKEN:
        raise ValueError(
            "TELEGRAM_TOKEN est introuvable."
        )

    init_db()

    app = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    register_game_handlers(app)
    register_verification_handlers(app)

    print("🤖 YOHAN PREDICTION BOT lancé.")

    app.run_polling()


if __name__ == "__main__":
    main()
