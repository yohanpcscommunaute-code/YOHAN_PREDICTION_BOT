from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from config import (
    MEGAPARI_REGISTER_URL,
    MEGAPARI_PROMO_CODE,
    MEGAPARI_MIN_DEPOSIT,
)


# ============================================================
# MESSAGE INSCRIPTION + DÉPÔT
# ============================================================

def megapari_message(language="fr"):

    texts = {

        "fr": (
            "🎯 <b>ACCÈS AU YOHAN PREDICTION BOT</b>\n\n"

            "Pour accéder aux fonctions du bot, "
            "tu dois effectuer les deux étapes suivantes :\n\n"

            "1️⃣ <b>Créer ton compte Megapari</b>\n"
            f"🎁 Code promo : <b>{MEGAPARI_PROMO_CODE}</b>\n\n"

            "2️⃣ <b>Effectuer le dépôt minimum demandé</b>\n"
            f"💰 Minimum : <b>{MEGAPARI_MIN_DEPOSIT} F</b>\n\n"

            "Après ces étapes, utilise les boutons "
            "de vérification ci-dessous.\n\n"

            "🔐 L'accès sera accordé uniquement lorsque "
            "les deux vérifications seront confirmées."
        ),

        "en": (
            "🎯 <b>YOHAN PREDICTION BOT ACCESS</b>\n\n"

            "To access the bot features, you must "
            "complete both steps:\n\n"

            "1️⃣ <b>Create your Megapari account</b>\n"
            f"🎁 Promo code: <b>{MEGAPARI_PROMO_CODE}</b>\n\n"

            "2️⃣ <b>Make the required minimum deposit</b>\n"
            f"💰 Minimum: <b>{MEGAPARI_MIN_DEPOSIT} F</b>\n\n"

            "After completing these steps, use the "
            "verification buttons below.\n\n"

            "🔐 Access will only be granted after "
            "both verifications are confirmed."
        ),
    }

    return texts.get(
        language,
        texts["fr"]
    )


# ============================================================
# CLAVIER
# ============================================================

def megapari_keyboard(language="fr"):

    labels = {

        "fr": {
            "register": "📝 S'INSCRIRE SUR MEGAPARI",
            "deposit": "💰 EFFECTUER LE DÉPÔT",
            "verify_registration": "✅ VÉRIFIER L'INSCRIPTION",
            "verify_deposit": "💳 VÉRIFIER LE DÉPÔT",
            "back": "↩️ RETOUR",
        },

        "en": {
            "register": "📝 REGISTER ON MEGAPARI",
            "deposit": "💰 MAKE DEPOSIT",
            "verify_registration": "✅ VERIFY REGISTRATION",
            "verify_deposit": "💳 VERIFY DEPOSIT",
            "back": "↩️ BACK",
        },
    }

    lang = labels.get(
        language,
        labels["fr"]
    )

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                lang["register"],
                url=MEGAPARI_REGISTER_URL
            )
        ],

        [
            InlineKeyboardButton(
                lang["deposit"],
                url=MEGAPARI_REGISTER_URL
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
