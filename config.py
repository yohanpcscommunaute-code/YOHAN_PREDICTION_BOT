import os

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError(
        "TELEGRAM_TOKEN n'est pas configuré."
    )

MEGAPARI_REGISTER_URL = os.getenv(
    "https://3773080.megapari-104631.in/",
    ""
)

MEGAPARI_PROMO_CODE = os.getenv(
    "MEGAPARI_PROMO_CODE",
    ""
)

MEGAPARI_MIN_DEPOSIT = float(
    os.getenv(
        "MEGAPARI_MIN_DEPOSIT",
        "25"
    )
)
