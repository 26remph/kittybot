import os

import requests
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)

load_dotenv()

# URL = 'https://api.thecatapi.com/v1/images/search'
URL = ''
NEW_URL = 'https://api.thedogapi.com/v1/images/search'

secret_token = os.getenv('TELEGRAM_TOKEN')


def get_new_image():
    try:
        response = requests.get(URL)
    except  Exception as e:
        print(e)
        response = requests.get(NEW_URL)

    response = response.json()
    random_cat = response[0].get('url')
    return random_cat


def say_hi(update: Update, context: CallbackContext):
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, я KittyBot!'
    )


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
    updater.dispatcher.add_handler(CommandHandler('new_cat', wake_up))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, say_hi))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
