import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telegram import Bot

from exceptions import SendMessageError, NotIndexError

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME: int = 600
TEST_DATE: int = 160000
ENDPOINT: str = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

HOMEWORK_VERDICTS: dict = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger()


def send_message(bot, message):
    """Отправка сообщения в Телеграмм."""
    logging.info(f'Starting to send message to reciver - {TELEGRAM_CHAT_ID}.')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception:
        raise SendMessageError(TELEGRAM_CHAT_ID)
    logging.info(f'Message was sent to reciver - {TELEGRAM_CHAT_ID}.')


def send_message_control(bot, message, pre_message):
    """Функция исключения повторения сообщений в чат."""
    if message != pre_message:
        send_message(bot, message)
    return message


def get_api_answer(current_timestamp: int) -> dict:
    """Запрос к серверу с результатами проверок домашних работ."""
    logging.info('Get_api_answer is starting.')
    timestamp = current_timestamp or int(time.time())
    params: dict = {'from_date': timestamp}
    headers: dict = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    get_data: dict = {'url': ENDPOINT, 'headers': headers, 'params': params}
    try:
        response = requests.get(**get_data)
        if response.status_code != HTTPStatus.OK:
            raise ConnectionError('Server does not exist.')
        return response.json()
    except Exception:
        raise ConnectionError('Server does not exist.')


def check_response(response) -> tuple:
    """Проверка соответвия ответа заданным параметрам."""
    logging.info('Check_response is starting.')
    if not isinstance(response, dict):
        raise TypeError('Received data type is not dict.')
    if ('homeworks' or 'current_date') not in response:
        raise NotIndexError('homeworks or current_date')
    homework = response.get('homeworks')
    current_date = response.get('current_date')
    if homework:
        logging.info('Changes have been found.')
        return homework[0], current_date
    logging.debug('Changes have been not found.')
    return homework, current_date


def parse_status(homework: dict) -> str:
    """Проверка изменения статуса проверки домашней работы."""
    logging.info('Parse_status is starting.')
    if 'homework_name' not in homework:
        raise KeyError('Homework_name not found.')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS:
        raise KeyError(f'Status {homework_status} not found.')
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Проверка наличия переменных в окружении."""
    logging.info('Check_tokens is starting.')
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical('There is no data in the environment. '
                         'The function is stopped.')
        raise sys.exit()
    logging.info('Main function is strating.')
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    pre_message: str = ""

    while True:
        try:
            logging.info(f'Check time from: {current_timestamp}')
            homework, current_date = check_response(
                get_api_answer(current_timestamp))
            if homework:
                message = parse_status(homework)
                pre_message = send_message_control(bot, message, pre_message)
            current_timestamp = current_date
            logging.info('Main function is waiting retry_time.')
        except Exception as error:
            message = f'Сбой в работе программы: {error} Смотри лог-файл.'
            logging.error(error)
            pre_message = send_message_control(bot, message, pre_message)
        finally:
            time.sleep(RETRY_TIME)


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
