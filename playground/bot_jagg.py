from environs import Env
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    Filters,
    MessageHandler,
)
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import os, sys
import django
DJANGO_PROJECT_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.append(DJANGO_PROJECT_PATH)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "self_storage.settings")
django.setup()

from django.template.loader import render_to_string
from django.forms.models import model_to_dict

from storage.models import User, Box, Promocodes


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
    if user.from_owner:
        button =[[InlineKeyboardButton("Посмотреть промокоды", callback_data='promos')],
                 [InlineKeyboardButton("Посмотреть просроченные боксы", callback_data='unpaid_boxes')]
                 ]
        reply_markup = InlineKeyboardMarkup(button)        
        update.message.reply_text(f'Здравствуйте {update.effective_user.username}', reply_markup=reply_markup)
        return 
    else:
        button =[[InlineKeyboardButton("Проверить заказы", callback_data='usuall_client')]]        
        reply_markup = InlineKeyboardMarkup(button)
        update.message.reply_text(f'Здравствуйте {update.effective_user.username}', reply_markup=reply_markup)
        return

def catch_responce(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()
    user, _ = User.objects.get_or_create(
        tg_username=update.effective_user.username,
        chat_id=update.effective_chat.id,
    )
    message = ''    
    if query.data=='usuall_client':
        boxes = user.boxes.all()
        for box in boxes:            
            message_html = render_to_string('client_boxes.html', {
                    'boxes': box
                })
            message = '\n'.join([message, message_html])
        context.bot.send_message(text=message,  chat_id=update.effective_chat.id, parse_mode=telegram.ParseMode.HTML)
        return
    if query.data=='promos':
        promos = Promocodes.objects.all()
        for promo in promos:            
            message_html = render_to_string('promos.html', {
                    'promo': promo
                })
            message = '\n'.join([message, message_html])
        context.bot.send_message(text=message,  chat_id=update.effective_chat.id, parse_mode=telegram.ParseMode.HTML)
    if query.data=='unpaid_boxes':
        current_datetime=datetime.datetime.now()
        boxes = Box.objects.filter(paid_till__lte=current_datetime).prefetch_related('user')
        for box in boxes:
            message_html = render_to_string('unpaid_boxes.html', {
                    'box': box
                })
            message = '\n'.join([message, message_html])
        context.bot.send_message(text=message,  chat_id=update.effective_chat.id, parse_mode=telegram.ParseMode.HTML)
        return


def message_handler(update, context):
    update.message.reply_text(f"Custom reply to message: '{update.message.text}'")


def error_handler_function(update, context):
    print(f"Update: {update} caused error: {context.error}")


def alert():
    env = Env()
    env.read_env()
    tg_token = env('TELEGRAM_TOKEN')    
    bot = telegram.Bot(token=tg_token)
    current_datetime = datetime.datetime.now()
    print(current_datetime)


if __name__ == '__main__':
    env = Env()
    env.read_env()
    tg_token = env('TELEGRAM_TOKEN')
    scheduler = BackgroundScheduler()
    scheduler.add_job(alert, 'interval', hours=24)
    scheduler.start()
    # Connecting our app with the Telegram API Key and using the context
    updater = Updater(tg_token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler("start", start))

    # Handing Incoming Messages
    updater.dispatcher.add_handler(MessageHandler(Filters.text, message_handler))
    updater.dispatcher.add_handler(
        CallbackQueryHandler(catch_responce)
    )

    # Error Handling if any
    updater.dispatcher.add_error_handler(error_handler_function)

    # Starting the bot using polling() function and check for messages every sec
    updater.start_polling(1.0)
    updater.idle()
