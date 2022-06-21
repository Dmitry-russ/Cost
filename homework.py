import logging
import os
import sys

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (CommandHandler, Updater, MessageHandler,
                          ConversationHandler, Filters)

from getapi import get_token, post_api, group_load, get_all_costs

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')

ENDPOINT: str = 'http://dmitrypetukhov90.pythonanywhere.com/api/v1/costs/'
GROUP_ENDPOINT: str = (
    'http://dmitrypetukhov90.pythonanywhere.com/api/v1/groups/')
USER_ENDPOINT: str = (
    'http://dmitrypetukhov90.pythonanywhere.com/auth/jwt/create/')

#  для хранения данных о введенном расходе на время выбора группы
COST: dict = {}
#  получаем доступ к api
API_TOKEN = get_token(USER_ENDPOINT, USER, PASSWORD)
logger = logging.getLogger()
ALL_GROUP, END = range(2)


def wake_up(update, context):
    """Приветствие."""
    chat_id = update.effective_chat.id
    username = update.message.chat.first_name
    context.bot.send_message(
        chat_id=chat_id,
        text=f'{username} привет! Я бот, который поможет тебе контролировать свои расходы.'
             f'Я могу работать только с целыми числами. Введи любое число, выбери категорию и все!'
             f'Для вывода статистики используй команду /check.',
    )
    logging.info(f'Пользователь {username}, {chat_id} запустил чат.')


def have_massege(update, context):
    """Обработка первичного сообщения о расходе."""
    chat = update.effective_chat
    text = update.message.text
    if text.isdigit():
        markup_key = ReplyKeyboardMarkup(
            [group_load(GROUP_ENDPOINT, API_TOKEN)], one_time_keyboard=True)
        update.message.reply_text(
            'Выберете категорию расхода. Для отмены нажмите /cancel.',
            reply_markup=markup_key, )
        COST[chat.id] = text
        return ALL_GROUP


def cost_download(update, _):
    """Основная функция сохранения даных в соответствии с группой расходов."""
    text = update.message.text
    chat = update.effective_chat
    group_in_text: list = ['Список групп расходов', ]
    group_in_text += group_load(GROUP_ENDPOINT, API_TOKEN)
    if text in group_in_text:
        group_id = group_in_text.index(text)
        cost = int(COST.get(chat.id))
        post_api(ENDPOINT, API_TOKEN, chat.id, cost, group_id)
        update.message.reply_text(
            f'Расход по категории "{text}" записан и составил: {cost}.',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    update.message.reply_text(
        'Категория не выбрана.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def cancel(update, _):
    """Отмена ввода расхода."""
    update.message.reply_text(
        'Ввод отменен.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def check_tokens() -> bool:
    """Проверка наличия переменных в окружении."""
    logging.info('Check_tokens is starting.')
    return all([TELEGRAM_BOT_TOKEN, ])


def check(update, context):
    """Запрос статистики расходов."""
    chat_id = update.effective_chat.id
    response = get_all_costs(ENDPOINT, chat_id, API_TOKEN)
    group_dict: dict = {r.get("group"): 0 for r in response.json()}
    for r in response.json():
        group_dict[r.get("group")] += int(r.get("cost"))
    group_dict["всего"] = sum(group_dict.values())
    for group in group_dict:
        text = f'Всего расходов по: {group}: {group_dict[group]} .'
        context.bot.send_message(chat_id=chat_id, text=text)


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical('There is no data in the environment. '
                         'The function is stopped.')
        raise sys.exit()
    logging.info('Main function is strating.')

    group_in_text: str = ""
    for group in group_load(GROUP_ENDPOINT, API_TOKEN):
        group_in_text += group + '|'

    updater = Updater(token=TELEGRAM_BOT_TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('check', check))
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text, have_massege)],
        states={
            ALL_GROUP: [
                MessageHandler(Filters.regex(f'^({group_in_text})$'),
                               cost_download)]},
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
