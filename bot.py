import os
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from config import (
    TELEGRAM_TOKEN,
    ADMIN_ID,
    LUCKY_JET_COOLDOWN,
    ROCKET_QUEEN_COOLDOWN,
    LUCKY_JET_IMAGE,
    ROCKET_QUEEN_IMAGE,
)

from database import (
    init_database,
    register_user,
    get_language,
    set_language,
    save_prediction,
    get_statistics,
)

from predictions import generate_prediction

from languages import TEXTS


# ============================================================
# MENUS
# ============================================================

def main_menu(lang):
    if lang == "en":
        keyboard = [
            ["🎮 GAMES"],
            ["🌐 LANGUAGE", "🆘 SUPPORT"],
            ["ℹ️ HOW IT WORKS"],
        ]
    else:
        keyboard = [
            ["🎮 JEUX"],
            ["🌐 LANGUE", "🆘 SUPPORT"],
            ["ℹ️ COMMENT ÇA MARCHE"],
        ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


def games_menu(lang):
    if lang == "en":
        keyboard = [
            ["✈️ LUCKY JET"],
            ["🚀 ROCKET QUEEN"],
            ["↩️ BACK"],
        ]
    else:
        keyboard = [
            ["✈️ LUCKY JET"],
            ["🚀 ROCKET QUEEN"],
            ["↩️ RETOUR"],
        ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


def language_menu():
    keyboard = [
        [
            "🇫🇷 Français",
            "🇬🇧 English",
        ],
        [
            "↩️ Retour",
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


def game_buttons(lang):
    if lang == "en":
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔮 GENERATE PREDICTION",
                    callback_data="generate",
                )
            ],
            [
                InlineKeyboardButton(
                    "🔄 NEXT ROUND",
                    callback_data="next",
                )
            ],
            [
                InlineKeyboardButton(
                    "↩️ MAIN MENU",
                    callback_data="main_menu",
                )
            ],
        ])

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔮 GÉNÉRER UNE PRÉDICTION",
                callback_data="generate",
            )
        ],
        [
            InlineKeyboardButton(
                "🔄 PROCHAIN TOUR",
                callback_data="next",
            )
        ],
        [
            InlineKeyboardButton(
                "↩️ MENU PRINCIPAL",
                callback_data="main_menu",
            )
        ],
    ])


# ============================================================
# CONFIGURATION DES JEUX
# ============================================================

GAMES = {
    "luckyjet": {
        "name": "LUCKY JET",
        "image": LUCKY_JET_IMAGE,
        "cooldown": LUCKY_JET_COOLDOWN,
        "text": "lucky",
    },

    "rocketqueen": {
        "name": "ROCKET QUEEN",
        "image": ROCKET_QUEEN_IMAGE,
        "cooldown": ROCKET_QUEEN_COOLDOWN,
        "text": "rocket",
    },
}


# ============================================================
# COOLDOWN
# ============================================================

def get_remaining_cooldown(
    context,
    game,
):
    """
    Chaque jeu possède sa propre minuterie.

    Lucky Jet :
    last_signal_luckyjet

    Rocket Queen :
    last_signal_rocketqueen
    """

    key = f"last_signal_{game}"

    last_signal = context.user_data.get(key)

    if not last_signal:
        return 0

    cooldown = GAMES[game]["cooldown"]

    elapsed = (
        datetime.now() - last_signal
    ).total_seconds()

    remaining = cooldown - elapsed

    if remaining <= 0:
        return 0

    return int(remaining)


# ============================================================
# AFFICHER LE JEU
# ============================================================

async def show_game(
    update,
    context,
    game,
):
    user = update.effective_user

    lang = get_language(user.id)

    context.user_data["game"] = game

    info = GAMES[game]

    text = TEXTS[lang][info["text"]]

    await update.message.reply_photo(
        photo=info["image"],
        caption=text,
        parse_mode="HTML",
        reply_markup=game_buttons(lang),
    )


# ============================================================
# GÉNÉRER LA PRÉDICTION
# ============================================================

async def create_prediction(
    message,
    user_id,
    context,
):
    game = context.user_data.get("game")

    if game not in GAMES:
        return

    lang = get_language(user_id)

    remaining = get_remaining_cooldown(
        context,
        game,
    )

    if remaining > 0:

        minutes = remaining // 60
        seconds = remaining % 60

        await message.reply_text(
            TEXTS[lang]["wait"].format(
                minutes=minutes,
                seconds=seconds,
            ),
            parse_mode="HTML",
        )

        return

    result = generate_prediction()

    signal_time = result["time"]
    odds = result["odds"]
    safe = result["safe"]

    # --------------------------------------------------------
    # IMPORTANT :
    # Le cooldown est enregistré uniquement pour CE jeu.
    # --------------------------------------------------------

    context.user_data[
        f"last_signal_{game}"
    ] = datetime.now()

    info = GAMES[game]

    save_prediction(
        user_id,
        game,
        odds,
        safe,
        signal_time,
    )

    text = TEXTS[lang]["prediction"].format(
        time=signal_time,
        odds=f"{odds:.2f}",
        safe=f"{safe:.2f}",
        game=info["name"],
    )

    await message.reply_photo(
        photo=info["image"],
        caption=text,
        parse_mode="HTML",
        reply_markup=game_buttons(lang),
    )


# ============================================================
# /START
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user

    register_user(user)

    context.user_data.clear()

    lang = get_language(user.id)

    await update.message.reply_text(
        TEXTS[lang]["welcome"],
        parse_mode="HTML",
        reply_markup=main_menu(lang),
    )


# ============================================================
# /HELP
# ============================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user

    register_user(user)

    lang = get_language(user.id)

    await update.message.reply_text(
        TEXTS[lang]["how"],
        parse_mode="HTML",
        reply_markup=main_menu(lang),
    )


# ============================================================
# ADMIN
# ============================================================

async def admin_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user_id = update.effective_user.id

    if ADMIN_ID == 0 or user_id != ADMIN_ID:
        await update.message.reply_text(
            "❌ Accès administrateur refusé."
        )
        return

    stats = get_statistics()

    text = TEXTS["fr"]["admin"].format(
        users=stats["users"],
        active=stats["active"],
        predictions=stats["predictions"],
        lucky=stats["lucky"],
        rocket=stats["rocket"],
        fr=stats["fr"],
        en=stats["en"],
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
    )


# ============================================================
# BOUTONS INLINE
# ============================================================

async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    await query.answer()

    user = query.from_user

    register_user(user)

    lang = get_language(user.id)

    if query.data in [
        "generate",
        "next",
    ]:

        await create_prediction(
            query.message,
            user.id,
            context,
        )

        return

    if query.data == "main_menu":

        context.user_data.pop(
            "game",
            None,
        )

        await query.message.reply_text(
            TEXTS[lang]["welcome"],
            parse_mode="HTML",
            reply_markup=main_menu(lang),
        )

        return


# ============================================================
# MESSAGES
# ============================================================

async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user

    register_user(user)

    lang = get_language(user.id)

    text = update.message.text

    # --------------------------------------------------------
    # JEUX
    # --------------------------------------------------------

    if text in [
        "🎮 JEUX",
        "🎮 GAMES",
    ]:

        await update.message.reply_text(
            TEXTS[lang]["games"],
            parse_mode="HTML",
            reply_markup=games_menu(lang),
        )

        return

    # --------------------------------------------------------
    # LANGUE
    # --------------------------------------------------------

    if text in [
        "🌐 LANGUE",
        "🌐 LANGUAGE",
    ]:

        await update.message.reply_text(
            TEXTS[lang]["language"],
            parse_mode="HTML",
            reply_markup=language_menu(),
        )

        return

    # --------------------------------------------------------
    # SUPPORT
    # --------------------------------------------------------

    if text == "🆘 SUPPORT":

        await update.message.reply_text(
            TEXTS[lang]["support"],
            parse_mode="HTML",
            reply_markup=main_menu(lang),
        )

        return

    # --------------------------------------------------------
    # COMMENT ÇA MARCHE
    # --------------------------------------------------------

    if text in [
        "ℹ️ COMMENT ÇA MARCHE",
        "ℹ️ HOW IT WORKS",
    ]:

        await update.message.reply_text(
            TEXTS[lang]["how"],
            parse_mode="HTML",
            reply_markup=main_menu(lang),
        )

        return

    # --------------------------------------------------------
    # CHANGEMENT DE LANGUE
    # --------------------------------------------------------

    if text == "🇫🇷 Français":

        set_language(
            user.id,
            "fr",
        )

        await update.message.reply_text(
            TEXTS["fr"]["language_changed"],
            reply_markup=main_menu("fr"),
        )

        return

    if text == "🇬🇧 English":

        set_language(
            user.id,
            "en",
        )

        await update.message.reply_text(
            TEXTS["en"]["language_changed"],
            reply_markup=main_menu("en"),
        )

        return

    # --------------------------------------------------------
    # LUCKY JET
    # --------------------------------------------------------

    if text == "✈️ LUCKY JET":

        await show_game(
            update,
            context,
            "luckyjet",
        )

        return

    # --------------------------------------------------------
    # ROCKET QUEEN
    # --------------------------------------------------------

    if text == "🚀 ROCKET QUEEN":

        await show_game(
            update,
            context,
            "rocketqueen",
        )

        return

    # --------------------------------------------------------
    # RETOUR
    # --------------------------------------------------------

    if text in [
        "↩️ RETOUR",
        "↩️ BACK",
        "↩️ Retour",
    ]:

        await update.message.reply_text(
            TEXTS[lang]["welcome"],
            parse_mode="HTML",
            reply_markup=main_menu(lang),
        )

        return


# ============================================================
# MAIN
# ============================================================

def main():

    if not TELEGRAM_TOKEN:
        raise ValueError(
            "TELEGRAM_TOKEN est introuvable."
        )

    init_database()

    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    # Commandes
    app.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    app.add_handler(
        CommandHandler(
            "help",
            help_command,
        )
    )

    app.add_handler(
        CommandHandler(
            "admin",
            admin_command,
        )
    )

    # Boutons inline
    app.add_handler(
        CallbackQueryHandler(
            callback_handler,
        )
    )

    # Menu classique
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler,
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
