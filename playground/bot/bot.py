from environs import Env
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    Filters,
    MessageHandler,
)

from django.shortcuts import get_object_or_404
from storage.models import User


def start(update: Update, context: CallbackContext):
    '''start command'''

    user = get_object_or_404(User, tg_username=update.effective_user.username)
    print(user)

    button = [
        [InlineKeyboardButton("Хочу купить бокс для хранения", callback_data='buy_box')],
        [InlineKeyboardButton("У меня уже есть бокс", callback_data='list_boxes')],
    ]

    reply_markup = InlineKeyboardMarkup(button)

    print(update.effective_chat.id)
    print(update.effective_user.username)
    update.message.reply_text('Отлично! Выбери подходящий вариант:', reply_markup=reply_markup)


def sends_boxing_info(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()

    if query.data:
        context.bot.send_message(text=query.data, chat_id=update.effective_chat.id)


def message_handler(update, context):
    update.message.reply_text(f"Custom reply to message: '{update.message.text}'")


def error_handler_function(update, context):
    print(f"Update: {update} caused error: {context.error}")


if __name__ == '__main__':
    env = Env()
    env.read_env()
    tg_token = env('TELEGRAM_TOKEN')

    # Connecting our app with the Telegram API Key and using the context
    updater = Updater(tg_token, use_context=True)
    my_dispatcher = updater.dispatcher

    # Adding CommandHandler from telegram.ext to handle defined functions/commands
    my_dispatcher.add_handler(CommandHandler("start", start))

    # Handing Incoming Messages
    my_dispatcher.add_handler(MessageHandler(Filters.text, message_handler))
    updater.dispatcher.add_handler(
        CallbackQueryHandler(sends_boxing_info)
    )

    # Error Handling if any
    my_dispatcher.add_error_handler(error_handler_function)

    # Starting the bot using polling() function and check for messages every sec
    updater.start_polling(1.0)
    updater.idle()