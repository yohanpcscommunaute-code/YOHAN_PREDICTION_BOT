from datetime import datetime, timedelta
from random import uniform, randint

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
    Génère une prédiction YOHAN PREDICTION.

    Les paramètres sont contrôlés depuis config.py.
    """

    minutes = randint(
        TIME_MINUTES_MIN,
        TIME_MINUTES_MAX
    )

    prediction_time = datetime.now() + timedelta(
        minutes=minutes
    )

    odds = round(
        uniform(ODDS_MIN, ODDS_MAX),
        2
    )

    safe = randint(
        SAFE_MIN,
        SAFE_MAX
    )

    return {
        "time": prediction_time.strftime("%H:%M"),
        "odds": odds,
        "safe": safe,
    }


def format_prediction(result):
    return (
        "🎯 <b>YOHAN PREDICTION</b>\n\n"
        f"⏰ Heure : <b>{result['time']}</b>\n"
        f"📈 Cote : <b>{result['odds']}x</b>\n"
        f"🛡️ Sécurité : <b>{result['safe']}%</b>\n\n"
        "⚠️ Signal indicatif — aucun résultat n'est garanti."
    )
