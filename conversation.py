import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)

FAST_GROUP, ALL_GROUP, = range(2)

def select_group(update, _):
    reply_keyboard = [['Проезд', 'Продукты', 'Другое']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        'Выберете категорию',
        reply_markup=markup_key,)
    chat_id = update.effective_chat.id
    username = update.message.chat.first_name
    k=update.message.text
    return FAST_GROUP

def select_group_all(update, _):
    reply_keyboard = [['Семья', 'Дом', 'Нет категории']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        'Выберете категорию',
        reply_markup=markup_key,)
    return ConversationHandler.END

def cancel(update, _):
    update.message.reply_text(
        'ввод отменен', 
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


