from environs import Env
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    Filters,
    MessageHandler,
    ConversationHandler,
)

import os, sys
import django
DJANGO_PROJECT_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.append(DJANGO_PROJECT_PATH)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "self_storage.settings")
django.setup()

from django.template.loader import render_to_string
from storage.models import User, Box, Promocodes


STATIC_PAGES = (
    'forbidden_cargo',
    'faq',
    'prices',
)

WEIGHT_RANGE = {
    'до 10кг': 10,
    'от 10 до 25кг': 25,
    'от 25 до 40кг': 40,
    'от 40 до 70кг': 70,
    'от 70 до 100кг': 100,
    'больше 100кг': 101,
    'Я не знаю :(': 'dontknow',
}

def get_template(template_name, template_context):
    template_filepath = f'{template_name}.html'
    return render_to_string(template_filepath, template_context)


def start(update: Update, context):

    user, _ = User.objects.get_or_create(
        tg_username=update.effective_user.username,
        chat_id=update.effective_chat.id,
    )

    context.bot_data['user'] = user

    has_boxes = user.boxes.all().count()
    reply_text = f'Здравствуйте {update.effective_user.username}'
    if user.from_owner:
        buttons = [
            [InlineKeyboardButton("Посмотреть промокоды", callback_data='owner_promos')],
            # [InlineKeyboardButton("Посмотреть просроченные боксы", callback_data='unpaid_boxes')],
        ]
    elif has_boxes:
        buttons = [
            [InlineKeyboardButton("Список ваших боксов", callback_data='client_listboxes')],
            [InlineKeyboardButton("Купить еще один бокс", callback_data='client_buy_box')],
        ]
    else:
        template_context = {'username': update.effective_user.username}
        reply_text = get_template('new_client_welcome', template_context)
        buttons = [
            [InlineKeyboardButton("Купить бокс", callback_data='client_buy_box')],
        ]

    reply_markup = InlineKeyboardMarkup(buttons)
    update.message.reply_text(reply_text, reply_markup=reply_markup)


def owner_promos(update: Update, context):
    query = update.callback_query
    query.answer()
    promos = Promocodes.objects.all()

    reply_text = 'Действующих промокодов нет'
    if promos:
        promo_html = [get_template('promos', {'promo': promo}) for promo in promos]
        reply_text = '\n'.join(promo_html)
    query.bot.send_message(text=reply_text, chat_id=update.effective_chat.id, parse_mode=ParseMode.HTML)


def client_listboxes(update: Update, context):
    query = update.callback_query
    query.answer()
    boxes = context.bot_data['user'].boxes.all()
    reply_text = 'Список ваших боксов\n'
    buttons = []
    for box in boxes:
        button_text = f'Бокс номер {box.id} размером {box.size}, оплачен по {box.paid_till}'
        buttons.append(
            [InlineKeyboardButton(button_text, callback_data=f'client_show_box_{box.id}')]
        )
    reply_markup = InlineKeyboardMarkup(buttons)
    query.bot.send_message(text=reply_text, reply_markup=reply_markup, chat_id=update.effective_chat.id)


def client_show_box(update: Update, context):
    query = update.callback_query
    query.answer()
    box_id = int(query.data.split('_')[-1])
    box = Box.objects.get(pk=box_id)
    context.bot_data['current_box'] = box

    reply_text = get_template('showbox', {'box': box})
    buttons = [
        [InlineKeyboardButton(f'Заказать доставку всех вещей', callback_data=f'123')],
        [InlineKeyboardButton(f'Заказать доставку части вещей', callback_data=f'123')],
        [InlineKeyboardButton(f'QR код чтобы забрать самостоятельно', callback_data=f'123')]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    query.bot.send_message(text=reply_text, reply_markup=reply_markup, chat_id=update.effective_chat.id)


def client_buy_box(update: Update, context):
    query = update.callback_query
    query.answer()

    reply_text = 'Укажите вес вещей, которые вы хотите хранить в боксе:'

    buttons = []
    for weight_k, weight_v in WEIGHT_RANGE.items():
        buttons.append(
            [InlineKeyboardButton(weight_k, callback_data=f'set_weight_{weight_v}')]
        )
    reply_markup = InlineKeyboardMarkup(buttons)
    query.bot.send_message(text=reply_text, reply_markup=reply_markup, chat_id=update.effective_chat.id)


def client_set_weight(update: Update, context):
    query = update.callback_query
    query.answer()

    weight = query.data.split('_')[-1]
    if weight == 'dontknow':
        reply_text = 'Не переживайте, наши грузчики взвесят ваш груз. ' \
                     'Однако будьте готовы к тому, что цена может измениться\n'
    else:
        WEIGHT_RANGE_REVERSED = {v: k for k, v in WEIGHT_RANGE.items()}
        reply_text = f'Вы указали вес {WEIGHT_RANGE_REVERSED[weight]}\n'

    reply_text += 'Теперь укажите объем груза'
    '''
    buttons = [
        [InlineKeyboardButton("до 0.1м³", callback_data=f'set_weight_lt10')],
        [InlineKeyboardButton("0-25кг", callback_data=f'set_weight_25')],
        [InlineKeyboardButton("25-40кг", callback_data=f'set_weight_40')],
        [InlineKeyboardButton("40-70кг", callback_data=f'set_weight_70')],
        [InlineKeyboardButton("70-100кг", callback_data=f'set_weight_100')],
        [InlineKeyboardButton("больше 100кг", callback_data=f'set_weight_gt100')],  # 200 кг
        [InlineKeyboardButton("Я не знаю :(", callback_data='set_weight_dont_know')],
    ]

    reply_markup = InlineKeyboardMarkup(buttons)
    query.bot.send_message(text=reply_text, reply_markup=reply_markup, chat_id=update.effective_chat.id)
    '''

def message_handler(update, context):
    update.message.reply_text(f"Custom reply to message: '{update.message.text}'")


def error_handler_function(update, context):
    print(f"Update: {update} caused error: {context.error}")


if __name__ == '__main__':
    env = Env()
    env.read_env()
    tg_token = env('TELEGRAM_TOKEN')

    updater = Updater(tg_token, use_context=True)
    app = updater.dispatcher

    # owner handlers
    app.add_handler(CallbackQueryHandler(owner_promos, pattern='^owner_promos$'))

    # existing client handlers
    app.add_handler(CallbackQueryHandler(client_listboxes, pattern='^client_listboxes$'))
    app.add_handler(CallbackQueryHandler(client_show_box, pattern='^client_show_box_'))

    # new box handlers
    app.add_handler(CallbackQueryHandler(client_buy_box, pattern='^client_buy_box$'))
    app.add_handler(CallbackQueryHandler(client_set_weight, pattern='^client_set_weight_'))


    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(Filters.text, message_handler))
    app.add_error_handler(error_handler_function)

    updater.start_polling(1.0)
    updater.idle()