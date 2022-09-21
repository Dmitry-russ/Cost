import logging
import os
import sys
import datetime

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (CommandHandler, Updater, MessageHandler,
                          ConversationHandler, Filters)

from getapi import (get_token, post_api,
                    group_load, get_all_costs)
from consts import ENDPOINT, GROUP_ENDPOINT, USER_ENDPOINT

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')

#  получаем доступ к api
#  добавь обработку ошибок!
API_TOKEN = get_token(USER_ENDPOINT, USER, PASSWORD)
logger = logging.getLogger()
SAVE, CHECK, END = range(3)


def wake_up(update, context):
    """Приветствие при запуске."""

    chat_id = update.effective_chat.id
    username = update.message.chat.first_name
    context.bot.send_message(
        chat_id=chat_id,
        text=f'{username} привет! Я бот, который поможет тебе '
             f'контролировать свои расходы. '
             f'Я могу работать только с целыми числами. '
             f'Введи любое число, выбери категорию и '
             f'я сохраню эти расходы в базу! '
             f'Для вывода статистики используй команду /check.',
    )
    logging.info(f'User {username}, {chat_id} is starting bot')


def have_massege(update, context):
    """Обработка первичного сообщения о расходе."""

    chat = update.effective_chat
    text = update.message.text
    logging.info(
        f'Just another new messege: {text} from: {chat.id} . '
        'Next step is check for digit.')

    if text.isdigit():
        logging.info(f'Bot has new digit messege: {text} from: {chat.id} .')
        markup_key = ReplyKeyboardMarkup(
            [group_load(GROUP_ENDPOINT, API_TOKEN)], one_time_keyboard=True,
            resize_keyboard=True)
        update.message.reply_text(
            'Выберете категорию расходов. Для отмены нажмите /cancel.',
            reply_markup=markup_key, )
        context.user_data["text"] = text
        logging.info(
            'Messege: {text} from: {chat.id} was saved befor choosing group.')
        return SAVE
    elif text == '/check':
        markup_key = ReplyKeyboardMarkup(
            [['Месяц', 'Неделя', 'День']], one_time_keyboard=True,
            resize_keyboard=True)
        update.message.reply_text(
            'Выберете период для расчета статистики. '
            'Для отмены нажмите /cancel.',
            reply_markup=markup_key, )
        return CHECK


def cost_save(update, context):
    """Основная функция сохранения даных в соответствии с группой расходов."""

    logging.info('Cost download is starting.')
    text = update.message.text
    chat = update.effective_chat
    group_in_text: list = group_load(GROUP_ENDPOINT, API_TOKEN)
    if text in group_in_text:
        cost = int(context.user_data["text"])
        post_api(ENDPOINT, API_TOKEN, chat.id, cost, text)
        update.message.reply_text(
            f'Расходы в сумме {cost} руб. запиcаны в категорию: "{text}" .',
            reply_markup=ReplyKeyboardRemove()
        )
        logging.info(
            f'Bot has made POST requiest to API with: {cost} from: {chat.id} .'
            )
        return ConversationHandler.END
    update.message.reply_text(
        'Категория не выбрана. '
        'Повторите ввод данных если хотите сохранить расходы.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def cancel(update, _):
    """Отмена ввода расхода."""

    update.message.reply_text(
        'Ввод отменен.',
        reply_markup=ReplyKeyboardRemove()
    )
    logging.info('Cancel button.')
    return ConversationHandler.END


def check(update, context):
    """Запрос статистики расходов по категориям."""

    text = update.message.text
    dt_now = datetime.date.today()
    data_select: dict = {
        'Месяц': 31,
        'Неделя': 7,
        'День': 0
    }
    past_date = dt_now - datetime.timedelta(days=data_select[text])
    logging.info('Check function is starting.')
    chat_id = update.effective_chat.id
    response = get_all_costs(ENDPOINT, chat_id, API_TOKEN)
    group_dict: dict = {}

    for r in response.json():
        date = datetime.datetime.strptime(
            r.get("pub_date"), '%Y-%m-%dT%H:%M:%S.%f%z')
        date = datetime.date(year=date.year, month=date.month, day=date.day)
        if date >= past_date:
            try:
                group_dict[r.get("group")] += int(r.get("cost"))
            except KeyError:
                group_dict[r.get("group")] = int(r.get("cost"))

    if group_dict:
        group_dict["Всего"] = sum(group_dict.values())
    else:
        context.bot.send_message(chat_id=chat_id, text='нет данных')
        return ConversationHandler.END
    text: str = 'Всего расходов по категориям: \n'
    for group in group_dict:
        text += (f'{group}: '
                 f'{group_dict[group]} руб. \n')
    update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardRemove()
        )
    logging.info(f'Message: {text} was sent to: {chat_id} .')
    return ConversationHandler.END


def check_tokens() -> bool:
    """Проверка наличия переменных в окружении."""

    logging.info('Check_tokens is starting.')
    return all([TELEGRAM_BOT_TOKEN, USER, PASSWORD])


def main():
    """Основная логика работы бота."""

    if not check_tokens():
        logging.critical('There is no data in the environment. '
                         'The function is stopped.')
        raise sys.exit()
    logging.info('Main function is strating.')

    updater = Updater(token=TELEGRAM_BOT_TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', wake_up))

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text, have_massege)],
        fallbacks=[CommandHandler('cancel', cancel)],
        states={
            SAVE: [
                MessageHandler(Filters.text, cost_save)],
            CHECK: [
                MessageHandler(Filters.text, check)]},
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
