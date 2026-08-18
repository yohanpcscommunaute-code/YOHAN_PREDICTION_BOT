import os


# =========================
# TELEGRAM
# =========================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

ADMIN_ID = int(
    os.getenv("ADMIN_ID", "0")
)


# =========================
# COOLDOWNS
# =========================

LUCKY_JET_COOLDOWN = 5 * 60

ROCKET_QUEEN_COOLDOWN = 5 * 60


# =========================
# PREDICTIONS
# =========================

TIME_MINUTES_MIN = 2
TIME_MINUTES_MAX = 5

ODDS_MIN = 9.80
ODDS_MAX = 19.80

SAFE_MIN = 2.00
SAFE_MAX = 5.00


# =========================
# IMAGES
# =========================

LUCKY_JET_IMAGE = (
    "https://i.ibb.co/yBSRtYvL/"
    "IMG-20260730-145755-681.jpg"
)

ROCKET_QUEEN_IMAGE = (
    "https://i.ibb.co/1xvTQr2/"
    "IMG-20260730-145743-615.jpg"
)
