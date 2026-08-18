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
# MENU DES LANGUES
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

    register_user(user)

    await send_message_clean(
        context,
        update.effective_chat.id,
        TEXTS["fr"]["welcome"],
        reply_markup=language_keyboard()
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

    # Après la langue :
    # inscription Megapari avant le menu principal.

    await delete_previous_message(
        context,
        query.message.chat_id
    )

    message = await context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=MENU_IMAGE,
        caption=megapari_message(
            language
        ),
        parse_mode="HTML",
        reply_markup=megapari_keyboard(
            language
        )
    )

    context.user_data[
        "last_bot_message_id"
    ] = message.message_id


# ============================================================
# MENU
# ============================================================

async def menu_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

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
# VERIFICATION MEGAPARI
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
        "⏳ <b>VÉRIFICATION</b>\n\n"
        "La vérification automatique sera activée "
        "après la connexion complète à l'API Megapari.\n\n"
        "Merci de patienter.",

        "en":
        "⏳ <b>VERIFICATION</b>\n\n"
        "Automatic verification will be enabled "
        "after the Megapari API integration is completed.\n\n"
        "Please wait.",
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

    # MENU JEUX
    app.add_handler(
        CallbackQueryHandler(
            games_callback,
            pattern=r"^games$"
        )
    )

    # CRASH
    app.add_handler(
        CallbackQueryHandler(
            crash_callback,
            pattern=r"^game_crash$"
        )
    )

    # AVIATOR
    app.add_handler(
        CallbackQueryHandler(
            aviator_callback,
            pattern=r"^game_aviator$"
        )
    )

    # LANGUE
    app.add_handler(
        CallbackQueryHandler(
            language_menu_callback,
            pattern=r"^language$"
        )
    )

    # SUPPORT
    app.add_handler(
        CallbackQueryHandler(
            support_callback,
            pattern=r"^support$"
        )
    )

    # COMMENT ÇA MARCHE
    app.add_handler(
        CallbackQueryHandler(
            how_callback,
            pattern=r"^how$"
        )
    )

    # MEGA GAMES
    app.add_handler(
        CallbackQueryHandler(
            mega_games_callback,
            pattern=r"^mega_games$"
        )
    )

    # VERIFICATION MEGAPARI
    app.add_handler(
        CallbackQueryHandler(
            verify_megapari_callback,
            pattern=r"^verify_megapari$"
        )
    )

    print(
        "🤖 YOHAN PREDICTION BOT démarré..."
    )

    app.run_polling()


# ============================================================
# LANCEMENT
# ============================================================

if __name__ == "__main__":
    main()
