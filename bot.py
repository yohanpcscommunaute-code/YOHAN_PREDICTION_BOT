from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ⚠️ Nous mettrons le token Telegram ici plus tard.
TOKEN = "TON_TOKEN_ICI"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bienvenue sur YOHAN PREDICTION BOT !\n\n"
        "🔥 Le bot est en préparation.\n"
        "Utilise /help pour voir les commandes."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 COMMANDES\n\n"
        "/start — Démarrer le bot\n"
        "/help — Afficher l'aide"
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    print("🤖 YOHAN PREDICTION BOT démarré...")
    app.run_polling()


if name == "main":
    main()
