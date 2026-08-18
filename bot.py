import os
import sqlite3
from datetime import datetime

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TELEGRAM_TOKEN")

DB = "bot.db"

BONUS_PARRAIN = 50
MIN_RETRAIT = 2000


# =========================
# BASE DE DONNÉES
# =========================

def db():
    return sqlite3.connect(DB)


def init_db():
    conn = db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            username TEXT,
            balance INTEGER DEFAULT 0,
            parrain INTEGER,
            date TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS retraits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            montant INTEGER,
            numero TEXT,
            date TEXT,
            statut TEXT
        )
    """)

    conn.commit()
    conn.close()


# =========================
# UTILISATEUR
# =========================

def get_user(user_id):
    conn = db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    )

    user = cursor.fetchone()

    conn.close()

    return user


def create_user(user, parrain=None):

    if get_user(user.id):
        return False

    conn = db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users
        (id, name, username, balance, parrain, date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user.id,
        user.first_name,
        user.username or "",
        0,
        parrain,
        datetime.now().strftime("%d/%m/%Y %H:%M")
    ))

    # Donner 50 F au parrain
    if parrain and parrain != user.id:

        cursor.execute(
            "SELECT id FROM users WHERE id = ?",
            (parrain,)
        )

        if cursor.fetchone():

            cursor.execute("""
                UPDATE users
                SET balance = balance + ?
                WHERE id = ?
            """, (
                BONUS_PARRAIN,
                parrain
            ))

    conn.commit()
    conn.close()

    return True


# =========================
# MENU
# =========================

def menu():

    keyboard = [
        ["💰 Mon solde", "💸 Retrait"],
        ["👥 Inviter", "❓ Aide"],
        ["👤 Mes parrainés"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    parrain = None

    if context.args:

        try:
            parrain = int(context.args[0])
        except:
            parrain = None

    nouveau = create_user(
        user,
        parrain
    )

    message = (
        "🤖 Bienvenue sur YOHAN PREDICTION BOT !\n\n"
        "🎁 Gagne de l'argent en invitant tes amis.\n"
        f"💰 Chaque filleul rapporte {BONUS_PARRAIN} F.\n\n"
        "👇 Choisis une option :"
    )

    await update.message.reply_text(
        message,
        reply_markup=menu()
    )


# =========================
# MON SOLDE
# =========================

async def solde(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = get_user(
        update.effective_user.id
    )

    if not user:
        await update.message.reply_text(
            "Utilise /start d'abord."
        )
        return

    await update.message.reply_text(
        "💰 MON SOLDE\n\n"
        f"👤 Nom : {user[1]}\n"
        f"🔗 Username : @{user[2] if user[2] else 'Aucun'}\n"
        f"🆔 ID : {user[0]}\n"
        f"💵 Solde : {user[3]} F\n"
        f"📅 Date d'adhésion : {user[5]}"
    )


# =========================
# INVITER
# =========================

async def inviter(update: Update, context: ContextTypes.DEFAULT_TYPE):

    bot = await context.bot.get_me()

    user_id = update.effective_user.id

    lien = f"https://t.me/{bot.username}?start={user_id}"

    await update.message.reply_text(
        "👥 INVITER\n\n"
        f"💰 Tu gagnes {BONUS_PARRAIN} F par filleul.\n\n"
        "🔗 Ton lien :\n"
        f"{lien}\n\n"
        "Partage ce lien à tes amis."
    )


# =========================
# MES PARRAINÉS
# =========================

async def parraines(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    conn = db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, username, date
        FROM users
        WHERE parrain = ?
    """, (
        user_id,
    ))

    users = cursor.fetchall()

    conn.close()

    if not users:

        await update.message.reply_text(
            "👤 MES PARRAINÉS\n\n"
            "Tu n'as encore aucun filleul."
        )

        return

    message = "👤 MES PARRAINÉS\n\n"

    for i, user in enumerate(users, 1):

        username = (
            f"@{user[1]}"
            if user[1]
            else "Aucun"
        )

        message += (
            f"{i}. {user[0]}\n"
            f"   {username}\n"
            f"   📅 {user[2]}\n\n"
        )

    await update.message.reply_text(
        message
    )


# =========================
# RETRAIT
# =========================

async def retrait(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = get_user(
        update.effective_user.id
    )

    if not user:
        return

    aujourd_hui = datetime.now().weekday()

    # Mercredi = 2
    # Jeudi = 3

    if aujourd_hui not in [2, 3]:

        await update.message.reply_text(
            "❌ Les retraits sont ouverts uniquement "
            "le mercredi et le jeudi."
        )

        return

    if user[3] < MIN_RETRAIT:

        await update.message.reply_text(
            "❌ Solde insuffisant.\n\n"
            f"💰 Ton solde : {user[3]} F\n"
            f"📌 Minimum : {MIN_RETRAIT} F"
        )

        return

    context.user_data["retrait"] = True

    await update.message.reply_text(
        f"💸 RETRAIT\n\n"
        f"💰 Ton solde : {user[3]} F\n"
        f"📌 Minimum : {MIN_RETRAIT} F\n\n"
        "Entre le montant à retirer :"
    )


# =========================
# TRAITEMENT DES MESSAGES
# =========================

async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text

    # RETRAIT EN COURS
    if context.user_data.get("retrait"):

        try:

            montant = int(text)

        except:

            await update.message.reply_text(
                "❌ Entre seulement un nombre.\n"
                "Exemple : 2000"
            )

            return

        user = get_user(
            update.effective_user.id
        )

        if montant < MIN_RETRAIT:

            await update.message.reply_text(
                f"❌ Le minimum est {MIN_RETRAIT} F."
            )

            return

        if montant > user[3]:

            await update.message.reply_text(
                "❌ Tu n'as pas assez d'argent."
            )

            return

        context.user_data["montant"] = montant
        context.user_data["retrait"] = False
        context.user_data["numero"] = True

        await update.message.reply_text(
            "📱 Entre maintenant le numéro "
            "sur lequel recevoir le retrait :"
        )

        return

    # NUMÉRO DE RETRAIT
    if context.user_data.get("numero"):

        numero = text

        montant = context.user_data["montant"]

        conn = db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO retraits
            (user_id, montant, numero, date, statut)
            VALUES (?, ?, ?, ?, ?)
        """, (
            update.effective_user.id,
            montant,
            numero,
            datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            ),
            "En attente"
        ))

        conn.commit()
        conn.close()

        context.user_data.clear()

        await update.message.reply_text(
            "✅ DEMANDE ENREGISTRÉE\n\n"
            f"💰 Montant : {montant} F\n"
            f"📱 Numéro : {numero}\n\n"
            "⏳ Ta demande est en attente de traitement."
        )

        return

    # MENU
    if text == "💰 Mon solde":
        await solde(update, context)

    elif text == "💸 Retrait":
        await retrait(update, context)

    elif text == "👥 Inviter":
        await inviter(update, context)

    elif text == "👤 Mes parrainés":
        await parraines(update, context)

    elif text == "❓ Aide":
        await update.message.reply_text(
            "📋 AIDE\n\n"
            "/start — Démarrer le bot\n\n"
            "💰 Mon solde — Voir ton argent\n\n"
            "💸 Retrait — Demander un retrait\n\n"
            "👥 Inviter — Inviter des amis\n\n"
            "👤 Mes parrainés — Voir tes filleuls\n\n"
            "📌 Retraits disponibles mercredi et jeudi.\n"
            f"📌 Minimum de retrait : {MIN_RETRAIT} F."
        )


# =========================
# MAIN
# =========================

def main():

    if not TOKEN:
        raise ValueError(
            "❌ TELEGRAM_TOKEN est introuvable. "
            "Vérifie le secret TELEGRAM_TOKEN dans GitHub."
        )

    init_db()

    app = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("help", 
                       lambda update, context:
                       help_command(update, context))
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    print(
        "🤖 YOHAN PREDICTION BOT démarré..."
    )

    app.run_polling()


async def help_command(update, context):
    await update.message.reply_text(
        "📋 COMMANDES\n\n"
        "/start — Démarrer le bot\n"
        "/help — Afficher l'aide"
    )


if __name__ == "__main__":
    main()
