from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher

from environs import Env
from telegram import Bot


def route(update, context):
    text = update.message.text

    # Control what your chatbot replies in this block of code!

    update.message.reply_text(text)

if __name__ == '__main__':
    env = Env()
    env.read_env()
    tg_token = env('TELEGRAM_TOKEN')

    updater = Updater(tg_token, use_context=True)
    updater.dispatcher.add_handler(MessageHandler(Filters.text, route))
    updater.start_polling()

    print("Your telegram bot is running!")

    updater.idle()