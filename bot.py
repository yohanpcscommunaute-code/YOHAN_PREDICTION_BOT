import os
import random
import sqlite3
from datetime import datetime, timedelta

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


# ============================================================
# CONFIGURATION
# ============================================================

TOKEN = os.getenv("TELEGRAM_TOKEN")

try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
except ValueError:
    ADMIN_ID = 0

DATABASE = "yohan_prediction.db"


# ============================================================
# COOLDOWN DES JEUX
# ============================================================
# IMPORTANT :
# Chaque jeu possède son propre cooldown.
# Les deux minuteries sont totalement indépendantes.

LUCKY_JET_COOLDOWN = 5       # minutes
ROCKET_QUEEN_COOLDOWN = 5    # minutes


# ============================================================
# PARAMÈTRES DES PRÉDICTIONS SIMULÉES
# ============================================================

TIME_MINUTES_MIN = 2
TIME_MINUTES_MAX = 5

ODDS_MIN = 9.80
ODDS_MAX = 19.80

SAFE_MIN = 2.00
SAFE_MAX = 5.00


# ============================================================
# IMAGES DES JEUX
# ============================================================

LUCKY_JET_IMAGE = (
    "https://i.ibb.co/yBSRtYvL/"
    "IMG-20260730-145755-681.jpg"
)

ROCKET_QUEEN_IMAGE = (
    "https://i.ibb.co/1xvTQr2/"
    "IMG-20260730-145743-615.jpg"
)


# ============================================================
# LANGUES
# ============================================================

TEXTS = {

    "fr": {

        "welcome":
            "✨ <b>YOHAN PREDICTION BOT</b> ✨\n\n"
            "Bienvenue sur notre plateforme de "
            "prédictions simulées.\n\n"
            "🎮 Choisis ton jeu et génère une "
            "prédiction de démonstration.\n\n"
            "⚠️ <b>AVERTISSEMENT</b>\n"
            "Les résultats affichés sont générés "
            "aléatoirement à titre démonstratif. "
            "Ils ne garantissent pas le résultat réel "
            "d'un jeu aléatoire.",

        "games":
            "🎮 <b>JEUX</b>\n\n"
            "Sélectionne un jeu :",

        "language":
            "🌐 <b>LANGUE</b>\n\n"
            "Choisis ta langue :",

        "support":
            "🆘 <b>SUPPORT</b>\n\n"
            "Pour toute question concernant le bot, "
            "contacte l'administrateur du projet.",

        "how":
            "ℹ️ <b>COMMENT ÇA MARCHE</b>\n\n"
            "1️⃣ Sélectionne un jeu.\n\n"
            "2️⃣ Appuie sur "
            "🔮 <b>GÉNÉRER UNE PRÉDICTION</b>.\n\n"
            "3️⃣ Le bot génère une simulation avec "
            "une heure, un coefficient ODDS et un "
            "niveau SAFE.\n\n"
            "4️⃣ Tu peux utiliser "
            "🔄 <b>PROCHAIN TOUR</b> lorsque le "
            "cooldown du jeu est terminé.\n\n"
            "⚠️ Ces résultats sont simulés et ne "
            "constituent pas une garantie de résultat.",

        "generate":
            "🔮 GÉNÉRER UNE PRÉDICTION",

        "next":
            "🔄 PROCHAIN TOUR",

        "menu":
            "↩️ MENU PRINCIPAL",

        "back":
            "↩️ RETOUR",

        "wait":
            "🤖 <b>RÉCUPÉRATION DES DONNÉES "
            "EN COURS...</b>\n\n"
            "Veuillez réessayer dans "
            "<b>{minutes} min {seconds} s</b>.",

        "prediction":
            "✨ <b>PRÉDICTIONS PREMIUM</b> ✨\n"
            "┏━━━━━━━━━━━\n"
            "┠ 《◆ TIME : {time} ⏰\n"
            "┠\n"
            "┠ 《◆ ODDS : {odds}X+ 🚀🚀\n"
            "┠\n"
            "┠ 《◆ SAFE : {safe}X+ ✅\n"
            "┗━━━━━━━━━━━\n\n"
            "🎮 Jeu : <b>{game}</b>\n\n"
            "⚠️ <i>Simulation à titre démonstratif. "
            "Ce signal ne garantit aucun résultat "
            "réel.</i>",

        "lucky":
            "✈️ <b>LUCKY JET</b>\n\n"
            "Système de prédiction simulée.\n\n"
            "⚠️ Les signaux sont générés "
            "aléatoirement à titre démonstratif.",

        "rocket":
            "🚀 <b>ROCKET QUEEN</b>\n\n"
            "Système de prédiction simulée.\n\n"
            "⚠️ Les signaux sont générés "
            "aléatoirement à titre démonstratif.",

        "language_changed":
            "🇫🇷 Langue française sélectionnée.",

        "not_registered":
            "❌ Utilise /start pour commencer.",

        "admin_denied":
            "❌ Accès administrateur refusé.",

        "admin":
            "👑 <b>PANNEAU ADMINISTRATION</b>\n\n"
            "👥 Utilisateurs : {users}\n"
            "🟢 Actifs 24h : {active}\n"
            "🔮 Prédictions : {predictions}\n\n"
            "✈️ LUCKY JET : {lucky}\n"
            "🚀 ROCKET QUEEN : {rocket}\n\n"
            "🇫🇷 Français : {fr}\n"
            "🇬🇧 English : {en}",
    },


    "en": {

        "welcome":
            "✨ <b>YOHAN PREDICTION BOT</b> ✨\n\n"
            "Welcome to our simulated prediction "
            "platform.\n\n"
            "🎮 Choose your game and generate a "
            "demonstration prediction.\n\n"
            "⚠️ <b>DISCLAIMER</b>\n"
            "Results are randomly generated for "
            "demonstration purposes. They do not "
            "guarantee the real outcome of a random game.",

        "games":
            "🎮 <b>GAMES</b>\n\n"
            "Select a game:",

        "language":
            "🌐 <b>LANGUAGE</b>\n\n"
            "Choose your language:",

        "support":
            "🆘 <b>SUPPORT</b>\n\n"
            "For any question about the bot, "
            "contact the project administrator.",

        "how":
            "ℹ️ <b>HOW IT WORKS</b>\n\n"
            "1️⃣ Select a game.\n\n"
            "2️⃣ Press "
            "🔮 <b>GENERATE PREDICTION</b>.\n\n"
            "3️⃣ The bot generates a simulation with "
            "a time, an ODDS coefficient and a SAFE level.\n\n"
            "4️⃣ You can use "
            "🔄 <b>NEXT ROUND</b> when the cooldown "
            "for that game is finished.\n\n"
            "⚠️ These results are simulated and do "
            "not guarantee any outcome.",

        "generate":
            "🔮 GENERATE PREDICTION",

        "next":
            "🔄 NEXT ROUND",

        "menu":
            "↩️ MAIN MENU",

        "back":
            "↩️ BACK",

        "wait":
            "🤖 <b>RETRIEVING DATA...</b>\n\n"
            "Please try again in "
            "<b>{minutes} min {seconds} sec</b>.",

        "prediction":
            "✨ <b>PREMIUM PREDICTIONS</b> ✨\n"
            "┏━━━━━━━━━━━\n"
            "┠ 《◆ TIME : {time} ⏰\n"
            "┠\n"
            "┠ 《◆ ODDS : {odds}X+ 🚀🚀\n"
            "┠\n"
            "┠ 《◆ SAFE : {safe}X+ ✅\n"
            "┗━━━━━━━━━━━\n\n"
            "🎮 Game: <b>{game}</b>\n\n"
            "⚠️ <i>Demonstration simulation. "
            "This signal does not guarantee any "
            "real outcome.</i>",

        "lucky":
            "✈️ <b>LUCKY JET</b>\n\n"
            "Simulated prediction system.\n\n"
            "⚠️ Signals are randomly generated "
            "for demonstration purposes.",

        "rocket":
            "🚀 <b>ROCKET QUEEN</b>\n\n"
            "Simulated prediction system.\n\n"
            "⚠️ Signals are randomly generated "
            "for demonstration purposes.",

        "language_changed":
            "🇬🇧 English language selected.",

        "not_registered":
            "❌ Use /start to begin.",

        "admin_denied":
            "❌ Administrator access denied.",

        "admin":
            "👑 <b>ADMIN PANEL</b>\n\n"
            "👥 Users: {users}\n"
            "🟢 Active 24h: {active}\n"
            "🔮 Predictions: {predictions}\n\n"
            "✈️ LUCKY JET: {lucky}\n"
            "🚀 ROCKET QUEEN: {rocket}\n\n"
            "🇫🇷 French: {fr}\n"
            "🇬🇧 English: {en}",
    }
}


# ============================================================
# BASE DE DONNÉES
# ============================================================

def get_db():
    return sqlite3.connect(DATABASE)


def init_database():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            username TEXT,
            language TEXT DEFAULT 'fr',
            predictions INTEGER DEFAULT 0,
            last_activity TEXT,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            game TEXT,
            odds REAL,
            safe REAL,
            signal_time TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# UTILISATEURS
# ============================================================

def register_user(user):

    conn = get_db()
    cursor = conn.cursor()

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute(
        "SELECT id FROM users WHERE id = ?",
        (user.id,)
    )

    exists = cursor.fetchone()

    if exists:

        cursor.execute("""
            UPDATE users
            SET name = ?,
                username = ?,
                last_activity = ?
            WHERE id = ?
        """, (
            user.first_name,
            user.username or "",
            now,
            user.id
        ))

    else:

        cursor.execute("""
            INSERT INTO users (
                id,
                name,
                username,
                language,
                predictions,
                last_activity,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user.id,
            user.first_name,
            user.username or "",
            "fr",
            0,
            now,
            now
        ))

    conn.commit()
    conn.close()


def get_language(user_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT language FROM users WHERE id = ?",
        (user_id,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return "fr"


def set_language(user_id, language):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET language = ?
        WHERE id = ?
    """, (
        language,
        user_id
    ))

    conn.commit()
    conn.close()


# ============================================================
# STATISTIQUES
# ============================================================

def save_prediction(
    user_id,
    game,
    odds,
    safe,
    signal_time
):

    conn = get_db()
    cursor = conn.cursor()

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        UPDATE users
        SET predictions = predictions + 1,
            last_activity = ?
        WHERE id = ?
    """, (
        now,
        user_id
    ))

    cursor.execute("""
        INSERT INTO predictions (
            user_id,
            game,
            odds,
            safe,
            signal_time,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        game,
        odds,
        safe,
        signal_time,
        now
    ))

    conn.commit()
    conn.close()


# ============================================================
# MENUS
# ============================================================

def main_menu(language):

    if language == "en":

        keyboard = [
            ["🎮 GAMES"],
            ["🌐 LANGUAGE", "🆘 SUPPORT"],
            ["ℹ️ HOW IT WORKS"]
        ]

    else:

        keyboard = [
            ["🎮 JEUX"],
            ["🌐 LANGUE", "🆘 SUPPORT"],
            ["ℹ️ COMMENT ÇA MARCHE"]
        ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


def games_menu(language):

    if language == "en":

        keyboard = [
            ["✈️ LUCKY JET"],
            ["🚀 ROCKET QUEEN"],
            ["↩️ BACK"]
        ]

    else:

        keyboard = [
            ["✈️ LUCKY JET"],
            ["🚀 ROCKET QUEEN"],
            ["↩️ RETOUR"]
        ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


def language_menu():

    keyboard = [
        [
            "🇫🇷 Français",
            "🇬🇧 English"
        ],
        [
            "↩️ Retour"
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


def game_buttons(language):

    if language == "en":

        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔮 GENERATE PREDICTION",
                    callback_data="generate"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔄 NEXT ROUND",
                    callback_data="next"
                )
            ],
            [
                InlineKeyboardButton(
                    "↩️ MAIN MENU",
                    callback_data="main_menu"
                )
            ]
        ])

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔮 GÉNÉRER UNE PRÉDICTION",
                callback_data="generate"
            )
        ],
        [
            InlineKeyboardButton(
                "🔄 PROCHAIN TOUR",
                callback_data="next"
            )
        ],
        [
            InlineKeyboardButton(
                "↩️ MENU PRINCIPAL",
                callback_data="main_menu"
            )
        ]
    ])


# ============================================================
# GÉNÉRATION SIMULÉE
# ============================================================

def generate_signal():

    random_minutes = random.randint(
        TIME_MINUTES_MIN,
        TIME_MINUTES_MAX
    )

    signal_date = (
        datetime.now()
        + timedelta(minutes=random_minutes)
    )

    signal_time = signal_date.strftime(
        "%H:%M"
    )

    odds_cents = random.randint(
        int(ODDS_MIN * 100),
        int(ODDS_MAX * 100)
    )

    odds = odds_cents / 100

    safe_cents = random.randint(
        int(SAFE_MIN * 100),
        int(SAFE_MAX * 100)
    )

    safe = safe_cents / 100

    return signal_time, odds, safe


# ============================================================
# COOLDOWN INDÉPENDANT
# ============================================================

def get_cooldown(game):

    if game == "luckyjet":
        return LUCKY_JET_COOLDOWN * 60

    if game == "rocketqueen":
        return ROCKET_QUEEN_COOLDOWN * 60

    return 0


def check_cooldown(
    context,
    game
):

    # Chaque jeu possède sa propre clé.
    #
    # Lucky Jet :
    # last_signal_luckyjet
    #
    # Rocket Queen :
    # last_signal_rocketqueen

    key = f"last_signal_{game}"

    last_time = context.user_data.get(key)

    if not last_time:
        return True, 0

    cooldown = get_cooldown(game)

    elapsed = (
        datetime.now() - last_time
    ).total_seconds()

    remaining = cooldown - elapsed

    if remaining <= 0:
        return True, 0

    return False, int(remaining)


# ============================================================
# AFFICHER UN JEU
# ============================================================

async def show_game(
    update,
    context,
    game
):

    user_id = update.effective_user.id

    language = get_language(user_id)

    context.user_data["game"] = game

    if game == "luckyjet":

        text = TEXTS[language]["lucky"]
        image = LUCKY_JET_IMAGE

    else:

        text = TEXTS[language]["rocket"]
        image = ROCKET_QUEEN_IMAGE

    await update.message.reply_photo(
        photo=image,
        caption=text,
        parse_mode="HTML",
        reply_markup=game_buttons(language)
    )


# ============================================================
# GÉNÉRER UNE PRÉDICTION
# ============================================================

async def generate_prediction(
    update,
    context
):

    user_id = update.effective_user.id

    language = get_language(user_id)

    game = context.user_data.get("game")

    if not game:

        await update.message.reply_text(
            TEXTS[language]["games"],
            parse_mode="HTML",
            reply_markup=games_menu(language)
        )

        return

    allowed, remaining = check_cooldown(
        context,
        game
    )

    if not allowed:

        minutes = remaining // 60
        seconds = remaining % 60

        await update.message.reply_text(
            TEXTS[language]["wait"].format(
                minutes=minutes,
                seconds=seconds
            )
        )

        return

    signal_time, odds, safe = generate_signal()

    # IMPORTANT :
    # On enregistre le cooldown uniquement
    # pour le jeu actuellement utilisé.

    context.user_data[
        f"last_signal_{game}"
    ] = datetime.now()

    if game == "luckyjet":

        game_name = "LUCKY JET"
        image = LUCKY_JET_IMAGE

    else:

        game_name = "ROCKET QUEEN"
        image = ROCKET_QUEEN_IMAGE

    message = TEXTS[language]["prediction"].format(
        time=signal_time,
        odds=f"{odds:.2f}",
        safe=f"{safe:.2f}",
        game=game_name
    )

    save_prediction(
        user_id,
        game,
        odds,
        safe,
        signal_time
    )

    await update.message.reply_photo(
        photo=image,
        caption=message,
        parse_mode="HTML",
        reply_markup=game_buttons(language)
    )


# ============================================================
# CALLBACK DES BOUTONS
# ============================================================

async def button_handler(
    update,
    context
):

    query = update.callback_query

    await query.answer()

    user = query.from_user

    register_user(user)

    language = get_language(user.id)

    data = query.data

    # ========================================================
    # GÉNÉRER / PROCHAIN TOUR
    # ========================================================

    if data in ["generate", "next"]:

        game = context.user_data.get("game")

        if not game:
            return

        allowed, remaining = check_cooldown(
            context,
            game
        )

        if not allowed:

            minutes = remaining // 60
            seconds = remaining % 60

            await query.message.reply_text(
                TEXTS[language]["wait"].format(
                    minutes=minutes,
                    seconds=seconds
                )
            )

            return

        signal_time, odds, safe = generate_signal()

        # ====================================================
        # COOLDOWN INDÉPENDANT
        # ====================================================

        context.user_data[
            f"last_signal_{game}"
        ] = datetime.now()

        if game == "luckyjet":

            game_name = "LUCKY JET"
            image = LUCKY_JET_IMAGE

        else:

            game_name = "ROCKET QUEEN"
            image = ROCKET_QUEEN_IMAGE

        message = TEXTS[language]["prediction"].format(
            time=signal_time,
            odds=f"{odds:.2f}",
            safe=f"{safe:.2f}",
            game=game_name
        )

        save_prediction(
            user.id,
            game,
            odds,
            safe,
            signal_time
        )

        await query.message.reply_photo(
            photo=image,
            caption=message,
            parse_mode="HTML",
            reply_markup=game_buttons(language)
        )

        return

    # =====
