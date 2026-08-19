from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🎯 Prédiction", callback_data="prediction"),
        ],
        [
            InlineKeyboardButton("📝 Inscription", callback_data="register"),
            InlineKeyboardButton("🔗 Lier mon compte", callback_data="link_account"),
        ],
        [
            InlineKeyboardButton("💰 Mon dépôt", callback_data="deposit"),
            InlineKeyboardButton("👤 Mon profil", callback_data="profile"),
        ],
        [
            InlineKeyboardButton("🔄 Actualiser", callback_data="refresh"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def registration_menu(register_url):
    keyboard = [
        [
            InlineKeyboardButton(
                "🎰 S'inscrire",
                url=register_url
            )
        ],
        [
            InlineKeyboardButton(
                "🔗 J'ai déjà un compte",
                callback_data="link_account"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Retour",
                callback_data="back_menu"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def back_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⬅️ Retour au menu",
                callback_data="back_menu"
            )
        ]
    ])
