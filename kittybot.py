import logging
import os

import requests
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)

load_dotenv()

# URL = 'https://api.thecatapi.com/v1/images/search'
# EXT_URL = 'https://api.thedogapi.com/v1/images/search'
URL = ''
EXT_URL = ''
STICKER_NOTHING_FOUND_ID = (
    'CAACAgIAAxkBAAEEiFBiYmlwjTAQX0ldw38OgYIL8LSXhgACOg8AAmyl2UkNNPZc7UiNvCQE'
)
PNG_NOTHING_FOUND = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)

secret_token = os.getenv('TELEGRAM_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def get_response_from_api():
    """
    Функция проверяет доступность API сервисов поставщиков картинок, следуя
    следующей логике: при доступности основного API, работаем только с ним,
    при отсутствии ответа, используем дополнительный.
    Нет доступных, бросаем исключение.
    """
    try:
        response = requests.get(URL)
    except Exception as e:
        logging.error(f'Ошибка при запросе к основному API {e}')
    else:
        return response

    try:
        response = requests.get(EXT_URL)
    except Exception as e:
        logging.error(f'Ошибка при запросе к дополнительному API {e}')
        raise APIException

    return response


class APIException(Exception):
    pass


def get_new_image():

    try:
        response = get_response_from_api()
    except APIException:
        return PNG_NOTHING_FOUND

    response = response.json()
    random_cat = response[0].get('url')

    return random_cat


def new_cat(update: Update, context: CallbackContext):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_new_image())


def wake_up(update: Update, context: CallbackContext):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['/new_cat']], resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        text=f'Привет, {name}. Посмотри какого котика я тебе нашла',
        reply_markup=button
    )

    context.bot.send_photo(chat.id, get_new_image())


def main():
    updater = Updater(token=secret_token)
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('new_cat', new_cat))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
