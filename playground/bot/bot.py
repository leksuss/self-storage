import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler, MessageHandler, Filters,
)

# Ведение журнала логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Этапы/состояния разговора
FIRST, SECOND = range(2)


def start(update, _):
    """Вызывается по команде `/start`."""
    # Получаем пользователя, который запустил команду `/start`
    user = update.message.from_user
    logger.info("Пользователь %s начал разговор", user.first_name)

    button = [
        [
            InlineKeyboardButton(
                "Уже есть бокс", callback_data='there is already a boxing'
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(button)
    update.message.reply_text('click on the button', reply_markup=reply_markup)
    return FIRST


def sends_boxing_info(update: Update, _) -> None:
    """Parses the CallbackQuery and updates the message text."""
    button = [
        [
            InlineKeyboardButton(
                "Забрать все вещи",
                callback_data='pick up all the things'
            ),
            InlineKeyboardButton(
                "Забрать часть вещей",
                callback_data='pick up some things'
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(button)
    query = update.callback_query
    query.answer()
    if query.data:
        query.edit_message_text(
            'Информация',
            reply_markup=reply_markup
        )
    return FIRST


def offers_ways_pick_up_things(update, _):
    """Показ нового выбора кнопок"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton(
                "Заберу сам", callback_data="i'll pick it up myself"
            ),
            InlineKeyboardButton(
                "Нужен курьер для доставки",
                callback_data="need a courier for delivery"
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if query.data == 'pick up all the things':
        query.edit_message_text(
            text="Выберите удобный способ забрать вещи",
            reply_markup=reply_markup
        )
        return FIRST
    query.edit_message_text(
        text="Выберите удобный способ забрать вещи \n"
             "Вещи можно будет вернуть, всё в порядке",
        reply_markup=reply_markup
    )
    return FIRST


def get_client_information(update, _):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text='Введите адрес доставки и желаемое время доставки'
    )
    return SECOND


def confirms_application(update, _):
    user = update.message.from_user
    logger.info("Пол %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Заявка принята. Нужен обратный звонок ? \n'
        '/yes или /no'
    )
    return FIRST


def sends_qar_code(update, _):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="генерация куар кода")
    return ConversationHandler.END


if __name__ == '__main__':
    updater = Updater('TOKEN')
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [
                CallbackQueryHandler(
                    sends_boxing_info,
                    pattern='^' + 'there is already a boxing' + '$'
                ),
                CallbackQueryHandler(
                    offers_ways_pick_up_things,
                    pattern='^' + 'pick up all the things' + '$'
                ),
                CallbackQueryHandler(
                    offers_ways_pick_up_things,
                    pattern='^' + 'pick up some things' + '$'
                ),
                CallbackQueryHandler(
                    sends_qar_code,
                    pattern='^' + "i'll pick it up myself" + '$'
                ),
                CallbackQueryHandler(
                    get_client_information,
                    pattern='^' + "need a courier for delivery" + '$'
                ),
            ],
            SECOND: [
                MessageHandler(Filters.text, confirms_application),
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()