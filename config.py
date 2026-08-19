import os


# ============================================================
# TELEGRAM
# ============================================================

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError(
        "TELEGRAM_TOKEN n'est pas configuré."
    )


# ============================================================
# MEGAPARI
# ============================================================

MEGAPARI_REGISTER_URL = os.getenv(
    "MEGAPARI_REGISTER_URL",
    "https://3773080.megapari-104631.in/"
)

MEGAPARI_PROMO_CODE = os.getenv(
    "MEGAPARI_PROMO_CODE",
    "SB55"
)

# Minimum réel demandé
MEGAPARI_MIN_DEPOSIT = float(
    os.getenv(
        "MEGAPARI_MIN_DEPOSIT",
        "5000"
    )
)


# ============================================================
# PREDICTIONS
# ============================================================

TIME_MINUTES_MIN = int(
    os.getenv(
        "TIME_MINUTES_MIN",
        "1"
    )
)

TIME_MINUTES_MAX = int(
    os.getenv(
        "TIME_MINUTES_MAX",
        "5"
    )
)

ODDS_MIN = float(
    os.getenv(
        "ODDS_MIN",
        "1.50"
    )
)

ODDS_MAX = float(
    os.getenv(
        "ODDS_MAX",
        "3.00"
    )
)

SAFE_MIN = int(
    os.getenv(
        "SAFE_MIN",
        "70"
    )
)

SAFE_MAX = int(
    os.getenv(
        "SAFE_MAX",
        "95"
    )
)


# ============================================================
# PAIEMENTS
# ============================================================

PAYMENT_MIN_AMOUNT = int(
    os.getenv(
        "PAYMENT_MIN_AMOUNT",
        "5000"
    )
)

PAYMENT_METHOD_MIXX = os.getenv(
    "PAYMENT_METHOD_MIXX",
    "Mixx by Yas"
)

PAYMENT_METHOD_MOOV = os.getenv(
    "PAYMENT_METHOD_MOOV",
    "Moov Money"
)


# ============================================================
# WEB GAMES V9
# ============================================================

WEB_GAMES_URL = os.getenv(
    "WEB_GAMES_URL",
    "https://example.com"
)
