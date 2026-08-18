from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import (
    MEGAPARI_REGISTER_URL,
    MEGAPARI_PROMO_CODE,
    MEGAPARI_MIN_DEPOSIT,
)


def megapari_message(language="fr"):
    """
    Message affiché avant l'accès au menu principal.
    """

    texts = {
        "fr": (
            "🎯 <b>ÉTAPE D'INSCRIPTION</b>\n\n"
            "Pour continuer, inscris-toi sur Megapari "
            "avec le code promo :\n\n"
            f"🎁 <b>{MEGAPARI_PROMO_CODE}</b>\n\n"
            f"💰 Dépôt minimum demandé : "
            f"<b>{MEGAPARI_MIN_DEPOSIT} F</b>\n\n"
            "Après ton inscription, utilise le bouton "
            "ci-dessous pour continuer."
        ),

        "en": (
            "🎯 <b>REGISTRATION</b>\n\n"
            "To continue, register on Megapari "
            "using the promo code:\n\n"
            f"🎁 <b>{MEGAPARI_PROMO_CODE}</b>\n\n"
            f"💰 Minimum deposit: "
            f"<b>{MEGAPARI_MIN_DEPOSIT} F</b>\n\n"
            "After registering, use the button "
            "below to continue."
        ),
    }

    return texts.get(
        language,
        texts["fr"]
    )


def megapari_keyboard(language="fr"):

    labels = {
        "fr": {
            "register": "📝 S'INSCRIRE SUR MEGAPARI",
            "verify": "✅ VÉRIFIER L'INSCRIPTION",
            "back": "↩️ RETOUR",
        },

        "en": {
            "register": "📝 REGISTER ON MEGAPARI",
            "verify": "✅ VERIFY REGISTRATION",
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
                lang["verify"],
                callback_data="verify_megapari"
            )
        ],

        [
            InlineKeyboardButton(
                lang["back"],
                callback_data="menu"
            )
        ],
    ])
