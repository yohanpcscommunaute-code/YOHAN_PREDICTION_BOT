import os

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from database import (
    init_database,
    register_user,
    get_language,
    set_language,
    is_user_fully_verified,
    is_registration_verified,
    is_deposit_verified,
)

from languages import TEXTS

from megapari import (
    megapari_message,
    megapari_keyboard,
)


# ============================================================
# CONFIGURATION
# ============================================================

TOKEN = os.getenv("TELEGRAM_TOKEN")

MENU_IMAGE = (
    "https://i.ibb.co/0RtRzkQZ/"
    "IMG-20260808-014512-643.jpg"
)


# ============================================================
# SUPPRESSION DES ANCIENS MESSAGES
# ============================================================

async def delete_previous_message(
    context,
    chat_id
):

    message_id = context.user_data.get(
        "last_bot_message_id"
    )

    if not message_id:
        return

    try:
        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
    except Exception:
        pass

    context.user_data.pop(
        "last_bot_message_id",
        None
    )


async def send_message_clean(
    context,
    chat_id,
    text,
    reply_markup=None,
    parse_mode="HTML"
):

    await delete_previous_message(
        context,
        chat_id
    )

    message = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=parse_mode,
        reply_markup=reply_markup
    )

    context.user_data[
        "last_bot_message_id"
    ] = message.message_id

    return message


# ============================================================
# PROTECTION CENTRALE
# ============================================================

async def require_full_verification(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    if is_user_fully_verified(user.id):
        return True

    language = get_language(user.id)

    registration_ok = is_registration_verified(
        user.id
    )

    deposit_ok = is_deposit_verified(
        user.id
    )

    if registration_ok and not deposit_ok:

        message = (
            "💰 <b>DÉPÔT REQUIS</b>\n\n"
            "Ton inscription est validée, "
            "mais ton dépôt n'est pas encore validé.\n\n"
            "Effectue le dépôt demandé puis "
            "utilise le bouton de vérification."
        )

    elif not registration_ok and deposit_ok:

        message = (
            "📝 <b>INSCRIPTION REQUISE</b>\n\n"
            "Ton dépôt est enregistré, "
            "mais ton inscription Megapari "
            "n'est pas encore validée.\n\n"
            "Effectue ton inscription puis "
            "utilise le bouton de vérification."
        )

    else:

        message = megapari_message(
            language
        )

    keyboard = megapari_keyboard(
        language
    )

    if update.callback_query:

        query = update.callback_query

        await query.answer(
            "⚠️ Accès non disponible.",
            show_alert=True
        )

        chat_id = query.message.chat_id

    else:

        chat_id = update.effective_chat.id

    await send_message_clean(
        context,
        chat_id,
        message,
        reply_markup=keyboard
    )

    return False


# ============================================================
# MENU PRINCIPAL
# ============================================================

async def send_menu(
    context,
    chat_id,
    language
):

    await delete_previous_message(
        context,
        chat_id
    )

    caption = TEXTS[language].get(
        "main_menu",
        "🎮 <b>MENU PRINCIPAL</b>"
    )

    message = await context.bot.send_photo(
        chat_id=chat_id,
        photo=MENU_IMAGE,
        caption=caption,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(language)
    )

    context.user_data[
        "last_bot_message_id"
    ] = message.message_id

    return message


def main_menu_keyboard(language):

    labels = {

        "fr": {
            "web": "🌐 MEGA GAMES WEB V9",
            "language": "🌐 LANGUE",
            "support": "🆘 SUPPORT",
            "how": "ℹ️ COMMENT ÇA MARCHE",
        },

        "en": {
            "web": "🌐 MEGA GAMES WEB V9",
            "language": "🌐 LANGUAGE",
            "support": "🆘 SUPPORT",
            "how": "ℹ️ HOW IT WORKS",
        },

        "es": {
            "web": "🌐 MEGA GAMES WEB V9",
            "language": "🌐 IDIOMA",
            "support": "🆘 SOPORTE",
            "how": "ℹ️ CÓMO FUNCIONA",
        },

        "la": {
            "web": "🌐 MEGA GAMES WEB V9",
            "language": "🌐 LINGUA",
            "support": "🆘 AUXILIUM",
            "how": "ℹ️ QUOMODO OPERATUR",
        },

        "ar": {
            "web": "🌐 MEGA GAMES WEB V9",
            "language": "🌐 اللغة",
            "support": "🆘 الدعم",
            "how": "ℹ️ كيف يعمل؟",
        },

        "pt": {
            "web": "🌐 MEGA GAMES WEB V9",
            "language": "🌐 IDIOMA",
            "support": "🆘 SUPORTE",
            "how": "ℹ️ COMO FUNCIONA",
        },

        "zh": {
            "web": "🌐 MEGA GAMES WEB V9",
            "language": "🌐 语言",
            "support": "🆘 客服",
            "how": "ℹ️ 使用方法",
        },

        "hi": {
            "web": "🌐 MEGA GAMES WEB V9",
            "language": "🌐 भाषा",
            "support": "🆘 सपोर्ट",
            "how": "ℹ️ यह कैसे काम करता है",
        },

        "ru": {
            "web": "🌐 MEGA GAMES WEB V9",
            "language": "🌐 ЯЗЫК",
            "support": "🆘 ПОДДЕРЖКА",
            "how": "ℹ️ КАК ЭТО РАБОТАЕТ",
        },
    }

    text = labels.get(
        language,
        labels["fr"]
    )

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "💥 CRASH",
                callback_data="game_crash"
            ),
            InlineKeyboardButton(
                "✈️ AVIATOR",
                callback_data="game_aviator"
            ),
        ],

        [
            InlineKeyboardButton(
                text["web"],
                callback_data="mega_games"
            )
        ],

        [
            InlineKeyboardButton(
                text["language"],
                callback_data="language"
            )
        ],

        [
            InlineKeyboardButton(
                text["support"],
                callback_data="support"
            )
        ],

        [
            InlineKeyboardButton(
                text["how"],
                callback_data="how"
            )
        ],
    ])


# ============================================================
# LANGUES
# ============================================================

def language_keyboard():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🇫🇷 Français",
                callback_data="lang_fr"
            ),
            InlineKeyboardButton(
                "🇬🇧 English",
                callback_data="lang_en"
            ),
        ],

        [
            InlineKeyboardButton(
                "🇪🇸 Español",
                callback_data="lang_es"
            ),
            InlineKeyboardButton(
                "🇻🇦 Latin",
                callback_data="lang_la"
            ),
        ],

        [
            InlineKeyboardButton(
                "🇸🇦 العربية",
                callback_data="lang_ar"
            ),
            InlineKeyboardButton(
                "🇵🇹 Português",
                callback_data="lang_pt"
            ),
        ],

        [
            InlineKeyboardButton(
                "🇨🇳 中文",
                callback_data="lang_zh"
            ),
            InlineKeyboardButton(
                "🇮🇳 हिन्दी",
                callback_data="lang_hi"
            ),
        ],

        [
            InlineKeyboardButton(
                "🇷🇺 Русский",
                callback_data="lang_ru"
            ),
        ],
    ])


# ============================================================
# START
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    # Création/mise à jour du profil Telegram.
    # Ceci NE valide PAS l'inscription.
    register_user(user)

    if is_user_fully_verified(user.id):

        language = get_language(
            user.id
        )

        await send_menu(
            context,
            update.effective_chat.id,
            language
        )

        return

    await send_message_clean(
        context,
        update.effective_chat.id,
        megapari_message("fr"),
        reply_markup=megapari_keyboard("fr")
    )


# ============================================================
# CHOIX DE LANGUE
# ============================================================

async def language_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    language = query.data.replace(
        "lang_",
        ""
    )

    set_language(
        user_id,
        language
    )

    if not await require_full_verification(
        update,
        context
    ):
        return

    await send_menu(
        context,
        query.message.chat_id,
        language
    )


# ============================================================
# MENU
# ============================================================

async def menu_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if not await require_full_verification(
        update,
        context
    ):
        return

    user_id = query.from_user.id

    language = get_language(
        user_id
    )

    await send_menu(
        context,
        query.message.chat_id,
        language
    )


# ============================================================
# LANGUE DEPUIS LE MENU
# ============================================================

async def language_menu_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if not await require_full_verification(
        update,
        context
    ):
        return

    await send_message_clean(
        context,
        query.message.chat_id,
        "🌐 <b>LANGUAGE / LANGUE</b>",
        reply_markup=language_keyboard()
    )


# ============================================================
# JEUX
# ============================================================

async def games_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if not await require_full_verification(
        update,
        context
    ):
        return

    user_id = query.from_user.id

    language = get_language(
        user_id
    )

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "💥 CRASH",
                callback_data="game_crash"
            ),
            InlineKeyboardButton(
                "✈️ AVIATOR",
                callback_data="game_aviator"
            ),
        ],

        [
            InlineKeyboardButton(
                TEXTS[language]["menu"],
                callback_data="menu"
            )
        ],
    ])

    await send_message_clean(
        context,
        query.message.chat_id,
        TEXTS[language].get(
            "games",
            "🎮 <b>JEUX</b>"
        ),
        reply_markup=keyboard
    )


# ============================================================
# CRASH
# ============================================================

async def crash_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if not await require_full_verification(
        update,
        context
    ):
        return

    user_id = query.from_user.id

    language = get_language(
        user_id
    )

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                TEXTS[language]["generate"],
                callback_data="generate_crash"
            )
        ],

        [
            InlineKeyboardButton(
                TEXTS[language]["menu"],
                callback_data="menu"
            )
        ],
    ])

    await send_message_clean(
        context,
        query.message.chat_id,
        TEXTS[language]["crash"],
        reply_markup=keyboard
    )


# ============================================================
# AVIATOR
# ============================================================

async def aviator_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if not await require_full_verification(
        update,
        context
    ):
        return

    user_id = query.from_user.id

    language = get_language(
        user_id
    )

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                TEXTS[language]["generate"],
                callback_data="generate_aviator"
            )
        ],

        [
            InlineKeyboardButton(
                TEXTS[language]["menu"],
                callback_data="menu"
            )
        ],
    ])

    await send_message_clean(
        context,
        query.message.chat_id,
        TEXTS[language]["aviator"],
        reply_markup=keyboard
    )


# ============================================================
# SUPPORT
# ============================================================

async def support_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if not await require_full_verification(
        update,
        context
    ):
        return

    user_id = query.from_user.id

    language = get_language(
        user_id
    )

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                TEXTS[language]["menu"],
                callback_data="menu"
            )
        ]
    ])

    await send_message_clean(
        context,
        query.message.chat_id,
        TEXTS[language]["support"],
        reply_markup=keyboard
    )


# ============================================================
# COMMENT ÇA MARCHE
# ============================================================

async def how_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if not await require_full_verification(
        update,
        context
    ):
        return

    user_id = query.from_user.id

    language = get_language(
        user_id
    )

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                TEXTS[language]["menu"],
                callback_data="menu"
            )
        ]
    ])

    await send_message_clean(
        context,
        query.message.chat_id,
        TEXTS[language]["how"],
        reply_markup=keyboard
    )


# ============================================================
# MEGA GAMES WEB V9
# ============================================================

async def mega_games_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if not await require_full_verification(
        update,
        context
    ):
        return

    user_id = query.from_user.id

    language = get_language(
        user_id
    )

    messages = {

        "fr":
        "🌐 <b>MEGA GAMES WEB V9</b>\n\n"
        "La Web App sera disponible prochainement.",

        "en":
        "🌐 <b>MEGA GAMES WEB V9</b>\n\n"
        "The Web App will be available soon.",
    }

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                TEXTS[language]["menu"],
                callback_data="menu"
            )
        ]
    ])

    await send_message_clean(
        context,
        query.message.chat_id,
        messages.get(
            language,
            messages["fr"]
        ),
        reply_markup=keyboard
    )


# ============================================================
# VÉRIFICATION INSCRIPTION
# ============================================================

async def verify_megapari_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    language = get_language(
        user_id
    )

    messages = {

        "fr":
        "🔎 <b>VÉRIFICATION DE L'INSCRIPTION</b>\n\n"
        "La vérification automatique n'est pas encore "
        "connectée à l'API Megapari.\n\n"
        "⚠️ Aucun accès ne sera accordé tant qu'une "
        "confirmation réelle de l'inscription n'est pas reçue.",

        "en":
        "🔎 <b>REGISTRATION VERIFICATION</b>\n\n"
        "Automatic verification is not yet connected "
        "to the Megapari API.\n\n"
        "⚠️ Access will not be granted until a real "
        "registration confirmation is received.",
    }

    await send_message_clean(
        context,
        query.message.chat_id,
        messages.get(
            language,
            messages["fr"]
        ),
        reply_markup=megapari_keyboard(language)
    )


# ============================================================
# VÉRIFICATION DÉPÔT
# ============================================================

async def verify_deposit_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    language = get_language(
        user_id
    )

    messages = {

        "fr":
        "🔎 <b>VÉRIFICATION DU DÉPÔT</b>\n\n"
        "La vérification automatique du dépôt n'est pas "
        "encore connectée au système de paiement.\n\n"
        "⚠️ Aucun dépôt ne sera marqué comme validé "
        "sans confirmation réelle.",

        "en":
        "🔎 <b>DEPOSIT VERIFICATION</b>\n\n"
        "Automatic deposit verification is not yet "
        "connected to the payment system.\n\n"
        "⚠️ No deposit will be marked as verified "
        "without real confirmation.",
    }

    await send_message_clean(
        context,
        query.message.chat_id,
        messages.get(
            language,
            messages["fr"]
        ),
        reply_markup=megapari_keyboard(language)
    )


# ============================================================
# MAIN
# ============================================================

def main():

    if not TOKEN:

        raise ValueError(
            "❌ TELEGRAM_TOKEN est introuvable.\n"
            "Vérifie le secret TELEGRAM_TOKEN dans GitHub."
        )

    init_database()

    app = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    # START
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # LANGUES
    app.add_handler(
        CallbackQueryHandler(
            language_callback,
            pattern=r"^lang_"
        )
    )

    # MENU
    app.add_handler(
        CallbackQueryHandler(
            menu_callback,
            pattern=r"^menu$"
        )
    )

    # JEUX
    app.add_handler(
        CallbackQueryHandler(
            games_callback,
            pattern=r"^games$"
        )
    )

    # CRASH
    app.add_handler(
        CallbackQueryH
