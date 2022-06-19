import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telegram import Bot

import logging
import os
from telegram import ReplyKeyboardMarkup, Bot
from telegram.ext import CommandHandler, Updater, MessageHandler, ConversationHandler, Filters

from exceptions import SendMessageError, NotIndexError

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')

ENDPOINT: str = 'http://dmitrypetukhov90.pythonanywhere.com/api/v1/costs/'
USER_ENDPOINT: str = 'http://dmitrypetukhov90.pythonanywhere.com/auth/jwt/create/'

response = requests.post(
        url= USER_ENDPOINT,
        data={'username': 'Dimons', 'password': 'Privet4545*',}
    ).json()
API_TOKEN =f'Bearer {response.get("access")}'


logger = logging.getLogger()


def check_tokens() -> bool:
    """Проверка наличия переменных в окружении."""
    logging.info('Check_tokens is starting.')
    return all([TELEGRAM_BOT_TOKEN,])

def have_massege(update, context):
    chat = update.effective_chat
    text = update.message.text
    if text.isdigit():
        requests.post(
            url= ENDPOINT,
            headers={'Authorization': API_TOKEN},
            data={'chat_id': chat.id, 'cost': int(text), 'group': 1}
        ).json()
        context.bot.send_message(
            chat_id=chat.id,
            text='Принято!',
        )

def wake_up(update, context):
    chat_id = update.effective_chat.id
    username = update.message.chat.first_name
    context.bot.send_message(
        chat_id=chat_id,
        text='Поехали!',
        )

def check(update, context):
    chat_id = update.effective_chat.id
    text = update.message.text
    response = requests.get(
        url= ENDPOINT+str(chat_id),
        headers={'Authorization': API_TOKEN},
        )
    summ: int  = 0
    for r in response.json():
        summ = summ+int(r.get("cost"))
    context.bot.send_message(
        chat_id=chat_id,
        text=f'Всего расходов: {summ}',
        )

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
    updater.dispatcher.add_handler(MessageHandler(Filters.text, have_massege))
    

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
