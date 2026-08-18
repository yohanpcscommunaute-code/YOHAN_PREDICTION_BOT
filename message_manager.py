from telegram import Message
from telegram.ext import ContextTypes


MESSAGE_KEY = "last_bot_message_id"


async def delete_previous_message(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
):
    message_id = context.user_data.get(MESSAGE_KEY)

    if not message_id:
        return

    try:
        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )
    except Exception:
        pass

    context.user_data.pop(
        MESSAGE_KEY,
        None,
    )


def remember_message(
    context: ContextTypes.DEFAULT_TYPE,
    message: Message,
):
    context.user_data[MESSAGE_KEY] = message.message_id


async def send_clean_message(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    text: str,
    **kwargs,
):
    await delete_previous_message(
        context,
        chat_id,
    )

    message = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        **kwargs,
    )

    remember_message(
        context,
        message,
    )

    return message


async def send_clean_photo(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    photo: str,
    caption: str,
    **kwargs,
):
    await delete_previous_message(
        context,
        chat_id,
    )

    message = await context.bot.send_photo(
        chat_id=chat_id,
        photo=photo,
        caption=caption,
        **kwargs,
    )

    remember_message(
        context,
        message,
    )

    return message
