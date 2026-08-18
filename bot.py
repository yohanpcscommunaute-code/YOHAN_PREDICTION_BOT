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


# ============================================================
# CONFIGURATION
# ============================================================

TOKEN = os.getenv("TELEGRAM_TOKEN")

MENU_IMAGE = (
    "https://i.ibb.co/0RtRzkQZ/"
    "IMG-20260808-014512-643.jpg"
)


# ============================================================
# GESTION DES MESSAGES
# ============================================================

async def delete_previous_message(
    context,
    chat_id
):
    """
    Supprime le dernier message envoyé par le bot
    à cet utilisateur.
    """

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
    """
    Supprime l'ancien message du bot,
    puis envoie un nouveau message.
    """

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


async def send_menu(
    context,
    chat_id,
    language
):
    """
    Supprime l'ancien message puis affiche
    l'image du menu principal avec ses boutons.
    """

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


# ============================================================
# TEXTES DU MENU
# ============================================================

def menu_labels(language):

    labels = {

        "fr": {
            "language": "🌐 LANGUE",
            "support": "🆘 SUPPORT",
            "how": "ℹ️ COMMENT ÇA MARCHE",
            "games": "🎮 JEUX",
            "web": "🌐 MEGA GAMES WEB V9",
        },

        "en": {
            "language": "🌐 LANGUAGE",
            "support": "🆘 SUPPORT",
            "how": "ℹ️ HOW IT WORKS",
            "games": "🎮 GAMES",
            "web": "🌐 MEGA GAMES WEB V9",
        },

        "es": {
            "language": "🌐 IDIOMA",
            "support": "🆘 SOPORTE",
            "how": "ℹ️ CÓMO FUNCIONA",
            "games": "🎮 JUEGOS",
            "web": "🌐 MEGA GAMES WEB V9",
        },

        "la": {
            "language": "🌐 LINGUA",
            "support": "🆘 AUXILIUM",
            "how": "ℹ️ QUOMODO OPERATUR",
            "games": "🎮 LUDI",
            "web": "🌐 MEGA GAMES WEB V9",
        },

        "ar": {
            "language": "🌐 اللغة",
            "support": "🆘 الدعم",
            "how": "ℹ️ كيف يعمل؟",
            "games": "🎮 الألعاب",
            "web": "🌐 MEGA GAMES WEB V9",
        },

        "pt": {
            "language": "🌐 IDIOMA",
            "support": "🆘 SUPORTE",
            "how": "ℹ️ COMO FUNCIONA",
            "games": "🎮 JOGOS",
            "web": "🌐 MEGA GAMES WEB V9",
        },

        "zh": {
            "language": "🌐 语言",
            "support": "🆘 客服",
            "how": "ℹ️ 使用方法",
            "games": "🎮 游戏",
            "web": "🌐 MEGA GAMES WEB V9",
        },

        "hi": {
            "language": "🌐 भाषा",
            "support": "🆘 सपोर्ट",
            "how": "ℹ️ यह कैसे काम करता है",
            "games": "🎮 गेम्स",
            "web": "🌐 MEGA GAMES WEB V9",
        },

        "ru": {
            "language": "🌐 ЯЗЫК",
            "support": "🆘 ПОДДЕРЖКА",
            "how": "ℹ️ КАК ЭТО РАБОТАЕТ",
            "games": "🎮 ИГРЫ",
            "web": "🌐 MEGA GAMES WEB V9",
        },
    }

    return labels.get(
        language,
        labels["fr"]
    )


# ============================================================
# MENU PRINCIPAL
# ============================================================

def main_menu_keyboard(language):

    labels = menu_labels(language)

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
                labels["web"],
                callback_data="mega_games"
            )
        ],

        [
            InlineKeyboardButton(
                labels["games"],
                callback_data="games"
            )
        ],

        [
            InlineKeyboardButton(
                labels["language"],
                callback_data="language"
            )
        ],

        [
            InlineKeyboardButton(
                labels["support"],
                callback_data="support"
            )
        ],

        [
            InlineKeyboardButton(
                labels["how"],
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
# MENU JEUX
# ============================================================

def games_keyboard(language):

    back_text = {

        "fr": "↩️ RETOUR",
        "en": "↩️ BACK",
        "es": "↩️ VOLVER",
        "la": "↩️ REDIRE",
        "ar": "↩️ رجوع",
        "pt": "↩️ VOLTAR",
        "zh": "↩️ 返回",
        "hi": "↩️ वापस",
        "ru": "↩️ НАЗАД",
    }.get(
        language,
        "↩️ RETOUR"
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
                back_text,
                callback_data="menu"
            )
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

    await send_menu(
        context,
        query.message.chat_id,
        language
    )


# ============================================================
# MENU PRINCIPAL
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

    await send_message_clean(
        context,
        query.message.chat_id,
        TEXTS[language]["games"],
        reply_markup=games_keyboard(
            language
        )
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
                TEXTS[language]["back"],
                callback_data="games"
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
                TEXTS[language]["back"],
                callback_data="games"
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
# CHOIX DE LANGUE
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

        "es":
        "🌐 <b>MEGA GAMES WEB V9</b>\n\n"
        "La Web App estará disponible próximamente.",

        "la":
        "🌐 <b>MEGA GAMES WEB V9</b>\n\n"
        "Applicatio interretialis mox praesto erit.",

        "ar":
        "🌐 <b>MEGA GAMES WEB V9</b>\n\n"
        "سيكون تطبيق الويب متاحاً قريباً.",

        "pt":
        "🌐 <b>MEGA GAMES WEB V9</b>\n\n"
        "A Web App estará disponível em breve.",

        "zh":
        "🌐 <b>MEGA GAMES WEB V9</b>\n\n"
        "Web App 即将推出。",

        "hi":
        "🌐 <b>MEGA GAMES WEB V9</b>\n\n"
        "Web App जल्द उपलब्ध होगी।",

        "ru":
        "🌐 <b>MEGA GAMES WEB V9</b>\n\n"
        "Web App скоро будет доступно.",
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
            "Vérifie le secret TELEGRAM_TOKEN."
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

    print(
        "🤖 YOHAN PREDICTION BOT démarré..."
    )

    app.run_polling()


# ============================================================
# LANCEMENT
# ============================================================

if __name__ == "__main__":
    main()
