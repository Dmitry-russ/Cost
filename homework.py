import logging
import sys
import os

import requests
from dotenv import load_dotenv

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from telegram.ext import CommandHandler, Updater, MessageHandler, ConversationHandler, Filters


load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')


ENDPOINT: str = 'http://dmitrypetukhov90.pythonanywhere.com/api/v1/costs/'
GROUP_ENDPOINT: str = 'http://dmitrypetukhov90.pythonanywhere.com/api/v1/groups/'
USER_ENDPOINT: str = 'http://dmitrypetukhov90.pythonanywhere.com/auth/jwt/create/'
COST: dict = {}

response = requests.post(
        url=USER_ENDPOINT,
        data={'username': 'Dimons', 'password': 'Privet4545*'}
    ).json()
API_TOKEN = f'Bearer {response.get("access")}'

logger = logging.getLogger()

ALL_GROUP, END = range(2)


def wake_up(update, context):
    chat_id = update.effective_chat.id
    username = update.message.chat.first_name
    context.bot.send_message(
        chat_id=chat_id,
        text=f'{username} привет! Я бот, который поможет тебе контролировать свои расходы.'
             f'Я могу работать только с целыми числами. введи любое число....',
        )


def have_massege(update, context):
    chat = update.effective_chat
    text = update.message.text
    if text.isdigit():
        group_in_text = group_load()
        reply_keyboard = [group_in_text]
        markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text(
            'Выберете категорию:',
            reply_markup=markup_key,)
        COST[chat.id] = text
        return ALL_GROUP


def select_group_all(update, _):
    text = update.message.text
    chat = update.effective_chat
    group_in_text = group_load()
    if text in group_in_text:
        group_id = group_in_text.index(text) + 1
        cost = int(COST.get(chat.id))
        requests.post(
            url=ENDPOINT,
            headers={'Authorization': API_TOKEN},
            data={'chat_id': chat.id, 'cost': cost, 'group': group_id}
        ).json()
        update.message.reply_text(
            f'Категория {text} принята.',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    update.message.reply_text(
        'Категория не выбрана.',
        reply_markup=ReplyKeyboardRemove()
        )
    return ConversationHandler.END


def end(update, _):
    update.message.reply_text(
        'Спасибо! Категория принята.',
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def cancel(update, _):
    update.message.reply_text(
        'ввод отменен',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def check_tokens() -> bool:
    """Проверка наличия переменных в окружении."""
    logging.info('Check_tokens is starting.')
    return all([TELEGRAM_BOT_TOKEN, ])


def check(update, context):
    chat_id = update.effective_chat.id
    #  text = update.message.text
    response = requests.get(
        url=ENDPOINT+str(chat_id),
        headers={'Authorization': API_TOKEN},
        )
    group_dict: dict = {r.get("group"): 0 for r in response.json()}
    sum = 0
    for r in response.json():
        group_dict[r.get("group")] += int(r.get("cost"))
        sum += int(r.get("cost"))
        text = []
    group_in_text = group_load()
    for group in group_dict:
        text = f'Всего расходов по группе {group_in_text[group-1]}: {group_dict[group]} .'
        context.bot.send_message(chat_id=chat_id, text=text)
    text = f'Всего расходов: {sum} .'
    context.bot.send_message(chat_id=chat_id, text=text)


def group_load():
    response = requests.get(
        url=GROUP_ENDPOINT,
        headers={'Authorization': API_TOKEN},
        )
    return [r.get("title") for r in response.json()]


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical('There is no data in the environment. '
                         'The function is stopped.')
        raise sys.exit()
    logging.info('Main function is strating.')

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    updater = Updater(token=TELEGRAM_BOT_TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('check', check))
    #  updater.dispatcher.add_handler(MessageHandler(Filters.text, have_massege))
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text, have_massege)],
        states={
            ALL_GROUP: [MessageHandler(Filters.regex('^(Проезд|Продукты|Разное)$'), select_group_all)],
            END: [MessageHandler(Filters.regex('^(Семья|Дом|Нет категории)$'), end)], },
        fallbacks=[CommandHandler('cancel', cancel)],
        )

    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='log.log',
        format=(
            '%(asctime)s, %(levelname)s, %(message)s,'
            '%(name)s, %(funcName)s, %(lineno)d'),
        filemode='a',
    )
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s, %(levelname)s, %(message)s,'
        '%(name)s, %(funcName)s, %(lineno)d')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    main()
