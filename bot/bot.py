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

import os, sys
import django
DJANGO_PROJECT_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.append(DJANGO_PROJECT_PATH)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "self_storage.settings")
django.setup()

from django.template.loader import render_to_string
from django.forms.models import model_to_dict

from storage.models import User, Box


STATIC_PAGES = (
    'forbidden_cargo',
    'faq',
    'prices',
)

def get_template(template_name, context):
    template_filepath = f'{template_name}.html'
    return render_to_string(template_filepath, context)


def start(update: Update, context: CallbackContext):

    user, _ = User.objects.get_or_create(
        tg_username=update.effective_user.username,
        chat_id=update.effective_chat.id,
    )

    boxes = user.boxes.all()
    if boxes:
        reply_text = 'Твои боксы:'
        button = []
        for box in boxes:
            button_name = f'бокс №{box.id}, размер {box.size}'
            button.append([InlineKeyboardButton(button_name, callback_data=f'showbox_{box.id}')])
    else:
        reply_text = 'У тебя пока нет боксов :('
        button = [
            [InlineKeyboardButton("Купить бокс", callback_data='buy_box')],
            [InlineKeyboardButton("Какие грузы мы не принимаем", callback_data='forbidden_cargo')],
            [InlineKeyboardButton("FAQ", callback_data='faq')],
            [InlineKeyboardButton("Цены", callback_data='prices')],
        ]

    reply_markup = InlineKeyboardMarkup(button)
    update.message.reply_text(reply_text, reply_markup=reply_markup)


def catch_responce(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()

    button = ''
    if query.data:
        if query.data == 'buy_box':
            reply_text = 'Укажи вес вещей, которые ты хочешь хранить в боксе'
            button = [
                [InlineKeyboardButton("до 10кг", callback_data=f'setweight_lt10')],
                [InlineKeyboardButton("10-25кг", callback_data=f'setweight_1025')],
                [InlineKeyboardButton("25-40кг", callback_data=f'setweight_2540')],
                [InlineKeyboardButton("40-70кг", callback_data=f'setweight_4070')],
                [InlineKeyboardButton("70-100кг", callback_data=f'setweight_70100')],
                [InlineKeyboardButton("больше 100кг", callback_data=f'setweight_gt100')],
                [InlineKeyboardButton("Я не знаю :(", callback_data='i_dont_know')],
            ]
        elif query.data in STATIC_PAGES:
            reply_text = get_template(query.data, '')
        elif query.data.startswith('showbox_'):
            box_id = query.data.split('_')[1]
            box = Box.objects.get(pk=box_id, user__tg_username=update.effective_user.username)
            box_context = model_to_dict(box)
            reply_text = get_template('showbox', box_context)
            button = [
                [InlineKeyboardButton("Изменить описание", callback_data='change_description')],
                [InlineKeyboardButton("Заказать доставку", callback_data='request_delivery')],
            ]
        else:
            reply_text = 'что-то еще'
        reply_markup = ''
        if button:
            reply_markup = InlineKeyboardMarkup(button)
        context.bot.send_message(text=reply_text,  reply_markup=reply_markup, chat_id=update.effective_chat.id)


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
        CallbackQueryHandler(catch_responce)
    )

    # Error Handling if any
    my_dispatcher.add_error_handler(error_handler_function)

    # Starting the bot using polling() function and check for messages every sec
    updater.start_polling(1.0)
    updater.idle()