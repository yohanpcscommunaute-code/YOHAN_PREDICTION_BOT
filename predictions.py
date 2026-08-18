import random
from datetime import datetime, timedelta

from config import (
    TIME_MINUTES_MIN,
    TIME_MINUTES_MAX,
    ODDS_MIN,
    ODDS_MAX,
    SAFE_MIN,
    SAFE_MAX,
)


def generate_prediction():
    """
    Génère une prédiction simulée.

    Le résultat est aléatoire et ne représente
    pas une prédiction réelle du résultat d'un jeu.
    """

    random_minutes = random.randint(
        TIME_MINUTES_MIN,
        TIME_MINUTES_MAX
    )

    signal_date = (
        datetime.now()
        + timedelta(minutes=random_minutes)
    )

    signal_time = signal_date.strftime("%H:%M")

    odds = random.randint(
        int(ODDS_MIN * 100),
        int(ODDS_MAX * 100)
    ) / 100

    safe = random.randint(
        int(SAFE_MIN * 100),
        int(SAFE_MAX * 100)
    ) / 100

    return {
        "time": signal_time,
        "odds": odds,
        "safe": safe,
  }
