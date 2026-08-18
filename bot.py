import os
import sqlite3
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
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
ADMIN_ID = os.getenv("ADMIN_ID")

REFERRAL_BONUS = 50
MIN_WITHDRAWAL = 2000

DB_FILE = "bot.db"


# ============================================================
# BASE DE DONNÉES
# ============================================================

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            balance INTEGER DEFAULT 0,
            phone TEXT,
            referred_by INTEGER,
            referral_paid INTEGER DEFAULT 0,
            joined_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            phone TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def get_user(user_id):
    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    conn.close()

    return user


def create_user(user, referred_by=None):
    conn = get_db()

    existing = conn.execute(
        "SELECT user_id FROM users WHERE user_id = ?",
        (user.id,)
    ).fetchone()

    if not existing:

        conn.execute("""
            INSERT INTO users (
                user_id,
                first_name,
                last_name,
                username,
                balance,
                referred_by,
                referral_paid,
                joined_at
            )
            VALUES (?, ?, ?, ?, 0, ?, 0, ?)
        """, (
            user.id,
            user.first_name or "",
            user.last_name or "",
            user.username or "",
            referred_by,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        ))

        conn.commit()

    conn.close()


def update_user_info(user):
    conn = get_db()

    conn.execute("""
        UPDATE users
        SET first_name = ?,
            last_name = ?,
            username = ?
        WHERE user_id = ?
    """, (
        user.first_name or "",
        user.last_name or "",
        user.username or "",
        user.id,
    ))

    conn.commit()
    conn.close()


# ============================================================
# MENU PRINCIPAL
# ============================================================

def main_keyboard():

    keyboard = [
        [
            KeyboardButton("💰 Mon solde"),
            KeyboardButton("💸 Retrait"),
        ],
        [
            KeyboardButton("👥 Inviter"),
            KeyboardButton("❓ Aide"),
        ],
        [
            KeyboardButton("👤 Mes parrainés"),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# ============================================================
# /START
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    referred_by = None

    # --------------------------------------------------------
    # RÉCUPÉRATION DU LIEN DE PARRAINAGE
    # --------------------------------------------------------

    if context.args:

        referral_code = context.args[0]

        if referral_code.startswith("ref_"):

            try:
                referred_by = int(
                    referral_code.replace(
                        "ref_",
                        ""
                    )
                )

            except ValueError:
                referred_by = None

    # Empêcher l'auto-parrainage
    if referred_by == user.id:
        referred_by = None

    existing = get_user(user.id)

    # --------------------------------------------------------
    # NOUVEL UTILISATEUR
    # --------------------------------------------------------

    if not existing:

        create_user(
            user,
            referred_by=referred_by
        )

        # ----------------------------------------------------
        # BONUS DU PARRAIN
        # ----------------------------------------------------

        if referred_by:

            # Vérifier que le parrain existe
            sponsor = get_user(referred_by)

            if sponsor:

                conn = get_db()

                conn.execute("""
                    UPDATE users
                    SET balance = balance + ?
                    WHERE user_id = ?
                """, (
                    REFERRAL_BONUS,
                    referred_by,
                ))

                conn.execute("""
                    UPDATE users
                    SET referral_paid = 1
                    WHERE user_id = ?
                """, (
                    user.id,
                ))

                conn.commit()
                conn.close()

                # Informer le parrain
                try:

                    await context.bot.send_message(
                        chat_id=referred_by,
                        text=(
                            "🎉 *NOUVEAU FILLEUL !*\n\n"
                            f"👤 {user.first_name} vient "
                            "de rejoindre votre équipe.\n\n"
                            f"💰 Bonus : +{REFERRAL_BONUS} F\n\n"
                            "Merci pour votre parrainage !"
                        ),
                        parse_mode="Markdown"
                    )

                except Exception as e:

                    print(
                        f"Impossible d'informer le parrain : {e}"
                    )

    else:

        update_user_info(user)

    # --------------------------------------------------------
    # MESSAGE D'ACCUEIL
    # --------------------------------------------------------

    await update.message.reply_text(
        "🤖 *Bienvenue sur YOHAN PREDICTION BOT !*\n\n"
        "🎁 Gagnez de l'argent en invitant vos amis.\n\n"
        f"💰 Chaque filleul vous rapporte "
        f"*{REFERRAL_BONUS} F*.\n\n"
        "👇 Choisissez une option dans le menu.",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )


# ============================================================
# MON SOLDE
# ============================================================

async def balance(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = get_user(
        update.effective_user.id
    )

    if not user:

        await update.message.reply_text(
            "❌ Votre compte n'existe pas encore.\n"
            "Utilisez /start."
        )

        return

    username = (
        f"@{user['username']}"
        if user["username"]
        else "Aucun"
    )

    await update.message.reply_text(
        "💰 *MON SOLDE*\n\n"
        f"👤 Nom : {user['first_name']} "
        f"{user['last_name'] or ''}\n"
        f"🔗 Username : {username}\n"
        f"🆔 ID Telegram : `{user['user_id']}`\n\n"
        f"💵 Solde : *{user['balance']} F*\n\n"
        f"📅 Date d'adhésion : "
        f"{user['joined_at']}",
        parse_mode="Markdown"
    )


# ============================================================
# INVITER
# ============================================================

async def invite(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    bot = await context.bot.get_me()

    referral_link = (
        f"https://t.me/{bot.username}"
        f"?start=ref_{user_id}"
    )

    await update.message.reply_text(
        "👥 *INVITER DES AMIS*\n\n"
        f"💰 Chaque personne qui rejoint avec "
        f"votre lien vous rapporte *{REFERRAL_BONUS} F*.\n\n"
        "🔗 *Votre lien personnel :*\n\n"
        f"`{referral_link}`\n\n"
        "📢 Partagez ce lien avec vos amis.",
        parse_mode="Markdown"
    )


# ============================================================
# MES PARRAINÉS
# ============================================================

async def my_referrals(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    conn = get_db()

    referrals = conn.execute("""
        SELECT *
        FROM users
        WHERE referred_by = ?
        ORDER BY joined_at DESC
    """, (
        user_id,
    )).fetchall()

    conn.close()

    if not referrals:

        await update.message.reply_text(
            "👤 *MES PARRAINÉS*\n\n"
            "Vous n'avez encore aucun filleul.",
            parse_mode="Markdown"
        )

        return

    text = "👤 *MES PARRAINÉS*\n\n"

    for index, referral in enumerate(
        referrals,
        1
    ):

        name = (
            referral["first_name"]
            or "Utilisateur"
        )

        username = (
            f"@{referral['username']}"
            if referral["username"]
            else "Aucun"
        )

        text += (
            f"{index}. 👤 {name}\n"
            f"   🔗 {username}\n"
            f"   🆔 `{referral['user_id']}`\n"
            f"   📅 {referral['joined_at']}\n\n"
        )

    text += (
        f"💰 Bonus par filleul : "
        f"{REFERRAL_BONUS} F"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown"
    )


# ============================================================
# AIDE
# ============================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "❓ *AIDE — YOHAN PREDICTION BOT*\n\n"
        "💰 *Mon solde*\n"
        "Voir votre solde et vos informations.\n\n"
        "💸 *Retrait*\n"
        "Demander un retrait de votre solde.\n\n"
        "👥 *Inviter*\n"
        "Obtenir votre lien personnel de parrainage.\n\n"
        "👤 *Mes parrainés*\n"
        "Voir les personnes que vous avez invitées.\n\n"
        "📌 *Parrainage*\n"
        f"Chaque nouveau filleul vous rapporte "
        f"{REFERRAL_BONUS} F.",
        parse_mode="Markdown"
    )


# ============================================================
# RETRAIT
# ============================================================

async def withdrawal_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    today = datetime.now().weekday()

    # Mercredi = 2
    # Jeudi = 3

    if today not in [2, 3]:

        await update.message.reply_text(
            "❌ *RETRAITS FERMÉS*\n\n"
            "Les retraits sont disponibles uniquement "
            "le *mercredi et le jeudi*.",
            parse_mode="Markdown"
        )

        return

    user = get_user(
        update.effective_user.id
    )

    if not user:

        await update.message.reply_text(
            "❌ Utilisateur introuvable.\n"
            "Utilisez /start."
        )

        return

    if user["balance"] < MIN_WITHDRAWAL:

        await update.message.reply_text(
            "❌ *SOLDE INSUFFISANT*\n\n"
            f"💰 Votre solde : {user['balance']} F\n"
            f"📌 Minimum de retrait : "
            f"{MIN_WITHDRAWAL} F",
            parse_mode="Markdown"
        )

        return

    context.user_data[
        "withdrawal_step"
    ] = "amount"

    await update.message.reply_text(
        "💸 *DEMANDE DE RETRAIT*\n\n"
        f"💰 Solde disponible : {user['balance']} F\n"
        f"📌 Montant minimum : {MIN_WITHDRAWAL} F\n\n"
        "👉 Entrez le montant que vous souhaitez retirer :",
        parse_mode="Markdown"
    )


# ============================================================
# TRAITEMENT DU RETRAIT
# ============================================================

async def process_withdrawal(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if "withdrawal_step" not in context.user_data:
        return

    user = get_user(
        update.effective_user.id
    )

    if not user:
        return

    step = context.user_data[
        "withdrawal_step"
    ]

    # ========================================================
    # ÉTAPE 1 : MONTANT
    # ========================================================

    if step == "amount":

        try:

            amount = int(
                update.message.text
                .replace(" ", "")
                .replace("F", "")
                .strip()
            )

        except ValueError:

            await update.message.reply_text(
                "❌ Montant invalide.\n\n"
                "Entrez uniquement le montant.\n"
                "Exemple : 2000"
            )

            return

        if amount < MIN_WITHDRAWAL:

            await update.message.reply_text(
                f"❌ Le montant minimum est "
                f"*{MIN_WITHDRAWAL} F*.",
                parse_mode="Markdown"
            )

            return

        if amount > user["balance"]:

            await update.message.reply_text(
                "❌ *SOLDE INSUFFISANT*\n\n"
                f"Votre solde est de "
                f"{user['balance']} F.",
                parse_mode="Markdown"
            )

            return

        context.user_data[
            "withdrawal_amount"
        ] = amount

        context.user_data[
            "withdrawal_step"
        ] = "phone"

        await update.message.reply_text(
            "📱 *NUMÉRO DE RÉCEPTION*\n\n"
            "Entrez le numéro sur lequel vous "
            "souhaitez recevoir votre argent.\n\n"
            "Exemple : `90XXXXXX`",
            parse_mode="Markdown"
        )

        return

    # ========================================================
    # ÉTAPE 2 : NUMÉRO
    # ========================================================

    if step == "phone":

        phone = update.message.text.strip()

        if len(phone) < 6:

            await update.message.reply_text(
                "❌ Numéro invalide.\n"
                "Veuillez entrer un numéro valide."
            )

            return

        amount = context.user_data[
            "withdrawal_amount"
        ]

        # ----------------------------------------------------
        # ENREGISTRER LA DEMANDE
        # ----------------------------------------------------

        conn = get_db()

        cursor = conn.execute("""
            INSERT INTO withdrawals (
                user_id,
                amount,
                phone,
                status,
                created_at
            )
            VALUES (?, ?, ?, 'pending', ?)
        """, (
            user["user_id"],
            amount,
            phone,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        ))

        withdrawal_id = cursor.lastrowid

        conn.execute("""
            UPDATE users
            SET phone = ?
            WHERE user_id = ?
        """, (
            phone,
            user["user_id"],
        ))

        conn.commit()
        conn.close()

        context.user_data.clear()

        # ----------------------------------------------------
        # INFORMATIONS ADMIN
        # ----------------------------------------------------

        username = (
            f"@{user['username']}"
            if user["username"]
            else "Aucun"
        )

        admin_text = (
            "💸 *NOUVELLE DEMANDE DE RETRAIT*\n\n"
            f"🆔 Demande : `{withdrawal_id}`\n\n"
            f"👤 Nom : {user['first_name']} "
            f"{user['last_name'] or ''}\n"
            f"🔗 Username : {username}\n"
            f"🆔 ID : `{user['user_id']}`\n\n"
            f"💰 Montant : *{amount} F*\n"
            f"📱 Numéro : `{phone}`\n\n"
            f"📅 Date : "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Valider",
                    callback_data=(
                        f"approve_{withdrawal_id}"
                    )
                ),
                InlineKeyboardButton(
                    "❌ Refuser",
                    callback_data=(
                        f"reject_{withdrawal_id}"
                    )
                ),
            ]
        ]

        try:

            await context.bot.send_message(
                chat_id=int(ADMIN_ID),
                text=admin_text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    keyboard
                )
            )

        except Exception as e:

            print(
                f"Erreur envoi administrateur : {e}"
            )

        await update.message.reply_text(
            "✅ *DEMANDE ENVOYÉE*\n\n"
            f"💰 Montant : {amount} F\n"
            f"📱 Numéro : {phone}\n\n"
            "⏳ Votre demande est maintenant "
            "en attente de validation.\n\n"
            "Vous recevrez un message lorsque "
            "l'administrateur aura traité votre demande.",
            parse_mode="Markdown",
            reply_markup=main_keyboard()
        )


# ============================================================
# VALIDATION / REFUS DU RETRAIT
# ============================================================

async def withdrawal_action(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    # --------------------------------------------------------
    # VÉRIFICATION ADMIN
    # --------------------------------------------------------

    if str(query.from_user.id) != str(ADMIN_ID):

        await query.answer(
            "❌ Vous n'êtes pas autorisé.",
            show_alert=True
        )

        return

    data = query.data

    # ========================================================
    # VALIDATION
    # ========================================================

    if data.startswith("approve_"):

        withdrawal_id = int(
            data.replace(
                "approve_",
                ""
            )
        )

        conn = get_db()

        withdrawal = conn.execute("""
            SELECT *
            FROM withdrawals
            WHERE id = ?
        """, (
            withdrawal_id,
        )).fetchone()

        if not withdrawal:

            conn.close()

            await query.edit_message_text(
                "❌ Demande introuvable."
            )

            return

        if withdrawal["status"] != "pending":

            conn.close()

            await query.answer(
                "Cette demande a déjà été traitée.",
                show_alert=True
            )

            return

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE user_id = ?
        """, (
            withdrawal["user_id"],
        )).fetchone()

        # ----------------------------------------------------
        # VÉRIFICATION DU SOLDE
        # ----------------------------------------------------

        if user["balance"] < withdrawal["amount"]:

            conn.execute("""
                UPDATE withdrawals
                SET status = 'rejected'
                WHERE id = ?
            """, (
                withdrawal_id,
            ))

            conn.commit()
            conn.close()

            await query.edit_message_
