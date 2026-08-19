from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from config import (
    MEGAPARI_REGISTER_URL,
    MEGAPARI_PROMO_CODE,
    MEGAPARI_MIN_DEPOSIT,
)


def megapari_message(language="fr"):

    if language == "en":
        return (
            "🎯 <b>YOHAN PREDICTION BOT</b>\n\n"
            "To access the prediction signals, complete "
            "the following steps:\n\n"
            "1️⃣ <b>Create your Megapari account</b>\n"
            f"🎁 Promo code: <b>{MEGAPARI_PROMO_CODE}</b>\n\n"
            "2️⃣ <b>Make the required deposit</b>\n"
            f"💰 Minimum: <b>{MEGAPARI_MIN_DEPOSIT} F</b>\n\n"
            "After completing the steps, use the verification "
            "buttons below.\n\n"
            "🔐 Access is unlocked only after verification."
        )

    return (
        "🎯 <b>ACCÈS AU YOHAN PREDICTION BOT</b>\n\n"
        "Pour accéder aux signaux de prédiction, "
        "tu dois effectuer les étapes suivantes :\n\n"
        "1️⃣ <b>Créer ton compte Megapari</b>\n"
        f"🎁 Code promo : <b>{MEGAPARI_PROMO_CODE}</b>\n\n"
        "2️⃣ <b>Effectuer le dépôt demandé</b>\n"
        f"💰 Minimum : <b>{MEGAPARI_MIN_DEPOSIT} F</b>\n\n"
        "Après avoir terminé les étapes, utilise les "
        "boutons de vérification ci-dessous.\n\n"
        "🔐 L'accès sera débloqué uniquement après "
        "confirmation des vérifications."
    )
def megapari_keyboard(language="fr"):

    labels = {
        "fr": {
            "register": "📝 S'INSCRIRE SUR MEGAPARI",
            "deposit": "💰 EFFECTUER LE DÉPÔT",
            "verify_registration": "✅ VÉRIFIER L'INSCRIPTION",
            "verify_deposit": "🔎 VÉRIFIER LE DÉPÔT",
            "back": "↩️ RETOUR",
        },

        "en": {
            "register": "📝 REGISTER ON MEGAPARI",
            "deposit": "💰 MAKE DEPOSIT",
            "verify_registration": "✅ VERIFY REGISTRATION",
            "verify_deposit": "🔎 VERIFY DEPOSIT",
            "back": "↩️ BACK",
        },
    }

    lang = labels.get(language, labels["fr"])

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                lang["register"],
                url=MEGAPARI_REGISTER_URL
            )
        ],

        [
            InlineKeyboardButton(
                "💰 DÉPÔT — MIXX BY YAS",
                callback_data="deposit_mixx"
            )
        ],

        [
            InlineKeyboardButton(
                "💰 DÉPÔT — MOOV MONEY",
                callback_data="deposit_moov"
            )
        ],

        [
            InlineKeyboardButton(
                lang["verify_registration"],
                callback_data="verify_megapari"
            )
        ],

        [
            InlineKeyboardButton(
                lang["verify_deposit"],
                callback_data="verify_deposit"
            )
        ],

        [
            InlineKeyboardButton(
                lang["back"],
                callback_data="menu"
            )
        ],
    ])

