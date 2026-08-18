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

from languages import (
    TEXTS,
    LANGUAGE_NAMES,
)

from message_manager import (
    send_clean_message,
)


# ============================================================
# CONFIGURATION
# ============================================================

TOKEN = os.getenv("TELEGRAM_TOKEN")


# ============================================================
# OUTILS
# ============================================================

def get_text(user_id, key, **kwargs):

    language = get_language(user_id)

    if language not in TEXTS:
        language = "fr"

    text = TEXTS[language].get(key, "")

    if kwargs:
        text = text.format(**kwargs)

    return text


# ============================================================
# BOUTON LANGUES
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
# MENU PRINCIPAL
# ============================================================

def main_menu_keyboard(language):

    t = TEXTS[language]

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🎮 " + (
                    "JEUX"
                    if language == "fr"
                    else "GAMES"
                    if language == "en"
                    else "JUEGOS"
                ),
                callback_data="games"
            )
        ],
        [
            InlineKeyboardButton(
                "🌐 " + (
                    "LANGUE"
                    if language == "fr"
                    else "LANGUAGE"
                    if language == "en"
                    else "IDIOMA"
                ),
                callback_data="language"
            )
        ],
        [
            InlineKeyboardButton(
                "🆘 " + t["support"].split("</b>")[0]
                .replace("🆘 <b>", ""),
                callback_data="support"
            )
        ],
        [
            InlineKeyboardButton(
                "ℹ️ " + (
                    "COMMENT ÇA MARCHE"
                    if language == "fr"
                    else "HOW IT WORKS"
                    if language == "en"
                    else "CÓMO FUNCIONA"
                ),
                callback_data="how"
            )
        ],
    ])


# ============================================================
# MENU DES JEUX
# ============================================================

def games_keyboard(language):

    if language == "fr":
        back_text = "↩️ RETOUR"

    elif language == "en":
        back_text = "↩️ BACK"

    elif language == "es":
        back_text = "↩️ VOLVER"

    else:
        back_text = "↩️ BACK"

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
# /START
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    register_user(user)

    text = get_text(
        user.id,
        "welcome"
    )

    await send_clean_message(
        context,
        update.effective_chat.id,
        text,
        parse_mode="HTML",
        reply_markup=language_keyboard(),
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

    text = (
        TEXTS[language]["language_selected"]
        + "\n\n"
        + TEXTS[language]["main_menu"]
    )

    await send_clean_message(
        context,
        query.message.chat_id,
        text,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(language),
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

    language = get_language(user_id)

    text = TEXTS[language]["main_menu"]

    await send_clean_message(
        context,
        query.message.chat_id,
        text,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(language),
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

    language = get_language(user_id)

    text = TEXTS[language]["games"]

    await send_clean_message(
        context,
        query.message.chat_id,
        text,
        parse_mode="HTML",
        reply_markup=games_keyboard(language),
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

    language = get_language(user_id)

    text = TEXTS[language]["crash"]

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

    await send_clean_message(
        context,
        query.message.chat_id,
        text,
        parse_mode="HTML",
        reply_markup=keyboard,
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

    language = get_language(user_id)

    text = TEXTS[language]["aviator"]

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

    await send_clean_message(
        context,
        query.message.chat_id,
        text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


# ============================================================
# LANGUE
# ============================================================

async def language_menu_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    await send_clean_message(
        context,
        query.message.chat_id,
        "🌐 <b>LANGUAGE / LANGUE</b>",
        parse_mode="HTML",
        reply_markup=language_keyboard(),
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

    language = get_language(user_id)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                TEXTS[language]["menu"],
                callback_data="menu"
            )
        ]
    ])

    await send_clean_message(
        context,
        query.message.chat_id,
        TEXTS[language]["support"],
        parse_mode="HTML",
        reply_markup=keyboard,
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

    language = get_language(user_id)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                TEXTS[language]["menu"],
                callback_data="menu"
            )
        ]
    ])

    await send_clean_message(
        context,
        query.message.chat_id,
        TEXTS[language]["how"],
        parse_mode="HTML",
        reply_markup=keyboard,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    if not TOKEN:

        raise ValueError(
            "TELEGRAM_TOKEN est introuvable. "
            "Ajoute le secret TELEGRAM_TOKEN."
        )

    init_database()

    app = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    # /start
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # Langues
    app.add_handler(
        CallbackQueryHandler(
            language_callback,
            pattern=r"^lang_"
        )
    )

    # Menu
    app.add_handler(
        CallbackQueryHandler(
            menu_callback,
            pattern=r"^menu$"
        )
    )

    # Jeux
    app.add_handler(
        CallbackQueryHandler(
            games_callback,
            pattern=r"^games$"
        )
    )

    # Crash
    app.add_handler(
        CallbackQueryHandler(
            crash_callback,
            pattern=r"^game_crash$"
        )
    )

    # Aviator
    app.add_handler(
        CallbackQueryHandler(
            aviator_callback,
            pattern=r"^game_aviator$"
        )
    )

    # Langue
    app.add_handler(
        CallbackQueryHandler(
            language_menu_callback,
            pattern=r"^language$"
        )
    )

    # Support
    app.add_handler(
        CallbackQueryHandler(
            support_callback,
            pattern=r"^support$"
        )
    )

    # Comment ça marche
    app.add_handler(
        CallbackQueryHandler(
            how_callback,
            pattern=r"^how$"
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
