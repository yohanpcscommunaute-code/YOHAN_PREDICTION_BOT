from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes,
)

from config import (
    PAYMENT_MIN_AMOUNT,
    PAYMENT_METHOD_MIXX,
    PAYMENT_METHOD_MOOV,
)

from payments import create_deposit


def payment_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🏠 MENU",
                callback_data="menu"
            )
        ]
    ])


async def choose_payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    method = (
        PAYMENT_METHOD_MIXX
        if query.data == "deposit_mixx"
        else PAYMENT_METHOD_MOOV
    )

    context.user_data["payment_method"] = method

    await query.message.reply_text(
        f"💰 <b>DÉPÔT — {method.upper()}</b>\n\n"
        f"Minimum : <b>{PAYMENT_MIN_AMOUNT} F</b>\n\n"
        "Envoie maintenant le montant que tu souhaites déposer.\n\n"
        "Exemple : <code>5000</code>",
        parse_mode="HTML",
    )


async def receive_amount(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    method = context.user_data.get("payment_method")

    if not method:
        return

    try:
        amount = float(
            update.message.text.replace(",", ".")
        )
    except ValueError:
        await update.message.reply_text(
            "❌ Montant invalide.\n\n"
            f"Minimum : <b>{PAYMENT_MIN_AMOUNT} F</b>",
            parse_mode="HTML"
        )
        return

    if amount < PAYMENT_MIN_AMOUNT:
        await update.message.reply_text(
            f"❌ Le dépôt minimum est "
            f"<b>{PAYMENT_MIN_AMOUNT} F</b>.",
            parse_mode="HTML"
        )
        return

    context.user_data["payment_amount"] = amount

    await update.message.reply_text(
        "🧾 <b>RÉFÉRENCE DE TRANSACTION</b>\n\n"
        f"Moyen : <b>{method}</b>\n"
        f"Montant : <b>{amount:.0f} F</b>\n\n"
        "Envoie maintenant la référence / ID "
        "de ta transaction.",
        parse_mode="HTML"
    )


async def receive_reference(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    method = context.user_data.get("payment_method")
    amount = context.user_data.get("payment_amount")

    if not method or not amount:
        return

    reference = update.message.text.strip()

    if len(reference) < 3:
        await update.message.reply_text(
            "❌ Référence invalide."
        )
        return

    create_deposit(
        telegram_id=update.effective_user.id,
        amount=amount,
        method=method,
        reference=reference
    )

    context.user_data.pop("payment_method", None)
    context.user_data.pop("payment_amount", None)

    await update.message.reply_text(
        "⏳ <b>DÉPÔT ENREGISTRÉ</b>\n\n"
        f"💰 Montant : <b>{amount:.0f} F</b>\n"
        f"📱 Moyen : <b>{method}</b>\n"
        f"🧾 Référence : <code>{reference}</code>\n\n"
        "Statut : <b>PENDING</b> ⏳\n\n"
        "Le dépôt doit être vérifié avant "
        "le déblocage des signaux.",
        parse_mode="HTML",
        reply_markup=payment_keyboard()
    )


def register_payment_handlers(app):

    app.add_handler(
        CallbackQueryHandler(
            choose_payment,
            pattern=r"^deposit_(mixx|moov)$"
        )
  )
