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

    if language == "en":
        register_text = "📝 REGISTER ON MEGAPARI"
        deposit_text = "💰 MAKE DEPOSIT"
        verify_register_text = "✅ VERIFY REGISTRATION"
        verify_deposit_text = "💳 VERIFY DEPOSIT"
        back_text = "↩️ BACK"
    else:
        register_text = "📝 S'INSCRIRE SUR MEGAPARI"
        deposit_text = "💰 EFFECTUER LE DÉPÔT"
        verify_register_text = "✅ VÉRIFIER L'INSCRIPTION"
        verify_deposit_text = "💳 VÉRIFIER LE DÉPÔT"
        back_text = "↩️ RETOUR"

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text=register_text,
                url=MEGAPARI_REGISTER_URL,
            )
        ],
        [
            InlineKeyboardButton(
                text=deposit_text,
                url=MEGAPARI_REGISTER_URL,
            )
        ],
        [
            InlineKeyboardButton(
                text=verify_register_text,
                callback_data="verify_registration",
            )
        ],
        [
            InlineKeyboardButton(
                text=verify_deposit_text,
                callback_data="verify_deposit",
            )
        ],
        [
            InlineKeyboardButton(
                text=back_text,
                callback_data="menu",
            )
        ],
    ])
