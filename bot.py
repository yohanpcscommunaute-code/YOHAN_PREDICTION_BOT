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
    init_db,
    create_user,
    get_user,
    get_language,
    set_language,
    can_access_signals,
)

from languages import TEXTS
from megapari import (
    megapari_message,
    megapari_keyboard,
)

from handlers.menu import main_menu_keyboard
from handlers.games import register_game_handlers


# ============================================================
# CONFIGURATION
# ============================================================

TOKEN = os.getenv("TELEGRAM_TOKEN")

MENU_IMAGE = (
    "https://i.ibb.co/0RtRzkQZ/"
    "IMG-20260808-014512-643.jpg"
)


# ============================================================
# MESSAGE PROPRE
# ============================================================

async def clean_send(
    context,
    chat_id,
    text,
    keyboard=None
):

    old_id = context.user_data.get(
        "last_bot_message_id"
    )

    if old_id:

        try:
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=old_id
            )
        except Exception:
            pass

    message = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML",
        reply_markup=keyboard
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

    old_id = context.user_data.get(
        "last_bot_message_id"
    )

    if old_id:

        try:
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=old_id
            )
        except Exception:
            pass

    texts = TEXTS.get(
        language,
        TEXTS["fr"]
    )

    caption = texts.get(
        "main_menu",
        "🎯 <b>YOHAN PREDICTION BOT</b>"
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
# CONTRÔLE D'ACCÈS
# ============================================================

async def require_access(
    update,
    context
):

    user_id = update.effective_user.id

    if can_access_signals(user_id):
        return True

    language = get_language(user_id)

    await clean_send(
        context,
        update.effective_chat.id,
        megapari_message(language),
        megapari_keyboard(language)
    )

    return False


# ============================================================
# START
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name
    )

    db_user = get_user(user.id)

    if not db_user:

        await clean_send(
            context,
            update.effective_chat.id,
            megapari_message("fr"),
            megapari_keyboard("fr")
        )

        return

    if not can_access_signals(user.id):

        await clean_send(
            context,
            update.effective_chat.id,
            megapari_message("fr"),
            megapari_keyboard("fr")
        )

        return

    language = get_language(user.id)

    await send_menu(
        context,
        update.effective_chat.id,
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

    if not await require_access(
        update,
        context
    ):
        return

    user_id = query.from_user.id

    language = get_language(user_id)

    await send_menu(
        context,
        query.message.chat_id,
        language
    )


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
                "🇵🇹 Português",
                callback_data="lang_pt"
            ),
        ],

        [
            InlineKeyboardButton(
                "🇷🇺 Русский",
                callback_data="lang_ru"
            ),
            InlineKeyboardButton(
                "🇸🇦 العربية",
                callback_data="lang_ar"
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
                "🇻🇦 Latin",
                callback_data="lang_la"
            ),
        ],

        [
            InlineKeyboardButton(
                "🏠 MENU",
                callback_data="menu"
            )
        ],
    ])


async def language_menu_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if not await require_access(
        update,
        context
    ):
        return

    await clean_send(
        context,
        query.message.chat_id,
        "🌐 <b>CHOISIS TA LANGUE</b>",
        language_keyboard()
    )


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

    if not await require_access(
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
# WEB GAMES V9
# ============================================================

async def web_games_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if not await require_access(
        update,
        context
    ):
        return

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🌐 OUVRIR WEB GAMES V9",
                url="https://example.com"
            )
        ],

        [
            InlineKeyboardButton(
                "🏠 MENU",
                callback_data="menu"
            )
        ],
    ])

    await clean_send(
        context,
        query.message.chat_id,
        "🌐 <b>WEB GAMES V9</b>\n\n"
        "Accède à la plateforme Web Games V9.",
        keyboard
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

    if not await require_access(
        update,
        context
    ):
        return

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🏠 MENU",
                callback_data="menu"
            )
        ]

    ])

    await clean_send(
        context,
        query.message.chat_id,
        "🆘 <b>SUPPORT</b>\n\n"
        "Contacte le support pour toute question.",
        keyboard
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

    if not await require_access(
        update,
        context
    ):
        return

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🏠 MENU",
                callback_data="menu"
            )
        ]

    ])

    await clean_send(
        context,
        query.message.chat_id,
        "ℹ️ <b>COMMENT ÇA MARCHE ?</b>\n\n"
        "1️⃣ Choisis ton jeu.\n"
        "2️⃣ Appuie sur 🎯 SIGNAL.\n"
        "3️⃣ Le bot génère un signal indicatif.\n\n"
        "⚠️ Aucun résultat n'est garanti.",
        keyboard
    )


# ============================================================
# VÉRIFICATION INSCRIPTION
# ============================================================

async def verify_registration_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer(
        "🔎 Vérification en attente.",
        show_alert=True
    )


# ============================================================
# VÉRIFICATION DÉPÔT
# ============================================================

async def verify_deposit_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer(
        "💰 Vérification du dépôt en attente.",
        show_alert=True
    )


# ============================================================
# MAIN
# ============================================================

def main():

    if not TOKEN:

        raise RuntimeError(
            "❌ TELEGRAM_TOKEN n'est pas configuré."
        )

    print("================================")
    print("🤖 YOHAN PREDICTION BOT")
    print("📡 Initialisation...")
    print("================================")

    init_db()

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

    # MENU
    app.add_handler(
        CallbackQueryHandler(
            menu_callback,
            pattern=r"^menu$"
        )
    )

    # LANGUE
    app.add_handler(
        CallbackQueryHandler(
            language_menu_callback,
            pattern=r"^language$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            language_callback,
            pattern=r"^lang_"
        )
    )

    # WEB GAMES V9
    app.add_handler(
        CallbackQueryHandler(
            web_games_callback,
            pattern=r"^web_games$"
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

    # VÉRIFICATION
    app.add_handler(
        CallbackQueryHandler(
            verify_registration_callback,
            pattern=r"^verify_registration$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            verify_deposit_callback,
            pattern=r"^verify_deposit$"
        )
    )

    # JEUX + SIGNAL
    register_game_handlers(app)

    print("✅ Bot connecté à Telegram.")
    print("🎯 Système SIGNAL chargé.")
    print("⏳ En attente des utilisateurs...")

    # IMPORTANT :
    # Garde le processus actif.
    app.run_polling(
        drop_pending_updates=True
    )


# ============================================================
# LANCEMENT
# ============================================================

if __name__ == "__main__":
    main()
