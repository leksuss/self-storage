import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    button = [
        [InlineKeyboardButton("Уже есть бокс", callback_data='boxing')]
    ]

    reply_markup = InlineKeyboardMarkup(button)
    update.message.reply_text('click on the button', reply_markup=reply_markup)


def sends_boxing_info(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()

    if query.data:
        context.bot.send_message(text='инфа', chat_id=update.effective_chat.id)


def help_command(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    update.message.reply_text("Use /start to test this bot.")


def main() -> None:
    updater = Updater('token')
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(
        CallbackQueryHandler(sends_boxing_info)
    )
    updater.dispatcher.add_handler(CommandHandler('help', help_command))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
