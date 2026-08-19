from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import ContextTypes


# ============================================================
# MENU PRINCIPAL
# ============================================================

def main_menu_keyboard(language="fr"):

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
                "🌐 WEB GAMES V9",
                callback_data="web_games"
            )
        ],

        [
            InlineKeyboardButton(
                "🌐 LANGUE",
                callback_data="language"
            )
        ],

        [
            InlineKeyboardButton(
                "🆘 SUPPORT",
                callback_data="support"
            )
        ],

        [
            InlineKeyboardButton(
                "ℹ️ COMMENT ÇA MARCHE",
                callback_data="how"
            )
        ],

    ])
