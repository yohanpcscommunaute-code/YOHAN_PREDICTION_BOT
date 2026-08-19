from database import get_user, update_user
from config import MIN_DEPOSIT


def get_verification_status(telegram_id):
    user = get_user(telegram_id)

    if not user:
        return {
            "exists": False,
            "registered": False,
            "deposit_verified": False,
            "signals_unlocked": False,
            "deposit": 0.0,
            "remaining": MIN_DEPOSIT,
        }

    deposit = float(user["deposit_amount"] or 0)

    registered = bool(user["registered"])
    deposit_verified = bool(user["deposit_verified"])

    unlocked = (
        registered
        and deposit_verified
        and deposit >= MIN_DEPOSIT
    )

    # On resynchronise le statut d'accès.
    if bool(user["signals_unlocked"]) != unlocked:
        update_user(
            telegram_id,
            signals_unlocked=int(unlocked)
        )

    return {
        "exists": True,
        "registered": registered,
        "one_win_user_id": user["one_win_user_id"],
        "deposit_verified": deposit_verified,
        "signals_unlocked": unlocked,
        "deposit": deposit,
        "remaining": max(0.0, MIN_DEPOSIT - deposit),
        "progress": min(100.0, (deposit / MIN_DEPOSIT) * 100),
    }


def can_use_prediction(telegram_id):
    status = get_verification_status(telegram_id)

    return (
        status["registered"]
        and status["deposit_verified"]
        and status["signals_unlocked"]
    )


def verification_message(telegram_id):
    status = get_verification_status(telegram_id)

    if not status["exists"]:
        return (
            "❌ Votre compte n'est pas encore enregistré.\n\n"
            "Utilisez /start pour commencer."
        )

    if not status["registered"]:
        return (
            "🔒 Accès aux prédictions verrouillé.\n\n"
            "📝 Vous devez d'abord terminer votre inscription."
        )

    if not status["deposit_verified"]:
        return (
            "🔒 Accès aux prédictions verrouillé.\n\n"
            "💰 Votre dépôt n'est pas encore vérifié.\n\n"
            f"Minimum requis : {MIN_DEPOSIT:.2f}"
        )

    if status["deposit"] < MIN_DEPOSIT:
        return (
            "🔒 Accès aux prédictions verrouillé.\n\n"
            f"💰 Dépôt actuel : {status['deposit']:.2f}\n"
            f"💰 Minimum requis : {MIN_DEPOSIT:.2f}\n"
            f"📉 Reste à déposer : {status['remaining']:.2f}"
        )

    return "✅ Votre accès aux prédictions est actif."
