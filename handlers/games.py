from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
)

from database import (
    get_language,
    can_access_signals,
)

from predictions import (
    generate_lucky_jet_prediction,
    generate_rocket_queen_prediction,
    format_prediction,
)


# ============================================================
# MENU JEUX
# ============================================================

def games_keyboard(language):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💥 LUCKY JET",
                callback_data="game_lucky"
            ),
            InlineKeyboardButton(
                "✈️ ROCKET QUEEN",
                callback_data="game_rocket"
            ),
        ],
        [
            InlineKeyboardButton(
                "🏠 MENU",
                callback_data="menu"
            )
        ],
    ])


# ============================================================
# LUCKY JET
# ============================================================

async def lucky_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if not can_access_signals(user_id):
        await query.answer(
            "🔒 Accès aux signaux non disponible.",
            show_alert=True
        )
        return

    language = get_language(user_id)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🎯 SIGNAL",
                callback_data="signal_lucky"
            )
        ],
        [
            InlineKeyboardButton(
                "🏠 MENU",
                callback_data="menu"
            )
        ],
    ])

    await query.edit_message_text(
        "💥 <b>LUCKY JET</b>\n\n"
        "🔥 Analyse prête.\n"
        "🎯 Appuie sur <b>SIGNAL</b> pour générer.",
        parse_mode="HTML",
        reply_markup=keyboard
    )


# ============================================================
# ROCKET QUEEN
# ============================================================

async def rocket_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if not can_access_signals(user_id):
        await query.answer(
            "🔒 Accès aux signaux non disponible.",
            show_alert=True
        )
        return

    language = get_language(user_id)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🎯 SIGNAL",
                callback_data="signal_rocket"
            )
        ],
        [
            InlineKeyboardButton(
                "🏠 MENU",
                callback_data="menu"
            )
        ],
    ])

    await query.edit_message_text(
        "✈️ <b>ROCKET QUEEN</b>\n\n"
        "⚡ Analyse prête.\n"
        "🎯 Appuie sur <b>SIGNAL</b> pour générer.",
        parse_mode="HTML",
        reply_markup=keyboard
    )


# ============================================================
# SIGNAL LUCKY JET
# ============================================================

async def lucky_signal_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer("🎯 Signal généré !")

    user_id = query.from_user.id

    if not can_access_signals(user_id):
        await query.answer(
            "🔒 Accès aux signaux non disponible.",
            show_alert=True
        )
        return

    result = generate_lucky_jet_prediction()

    text = (
        "🔥 <b>SIGNAL LUCKY JET</b>\n\n"
        + format_prediction(result)
        + "\n\n"
        "⚡ Bonne chance !"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🎯 NOUVEAU SIGNAL",
                callback_data="signal_lucky"
            )
        ],
        [
            InlineKeyboardButton(
                "🏠 MENU",
                callback_data="menu"
            )
        ],
    ])

    await query.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=keyboard
    )


# ============================================================
# SIGNAL ROCKET QUEEN
# ============================================================

async def rocket_signal_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer("🎯 Signal généré !")

    user_id = query.from_user.id

    if not can_access_signals(user_id):
        await query.answer(
            "🔒 Accès aux signaux non disponible.",
            show_alert=True
        )
        return

    result = generate_rocket_queen_prediction()

    text = (
        "⚡ <b>SIGNAL ROCKET QUEEN</b>\n\n"
        + format_prediction(result)
        + "\n\n"
        "🚀 Bonne chance !"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🎯 NOUVEAU SIGNAL",
                callback_data="signal_rocket"
            )
        ],
        [
            InlineKeyboardButton(
                "🏠 MENU",
                callback_data="menu"
            )
        ],
    ])

    await query.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=keyboard
    )


# ============================================================
# ENREGISTREMENT DES HANDLERS
# ============================================================

def register_game_handlers(app):

    app.add_handler(
        CallbackQueryHandler(
            lucky_callback,
            pattern=r"^game_lucky$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            rocket_callback,
            pattern=r"^game_rocket$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            lucky_signal_callback,
            pattern=r"^signal_lucky$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            rocket_signal_callback,
            pattern=r"^signal_rocket$"
        )
  )
