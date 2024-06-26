import asyncio
import logging
import sys
import sqlite3
import xml.etree.ElementTree as ET
import requests

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

DB_FILE = 'user_states.db'

url = 'https://www.cbr.ru/scripts/XML_daily.asp'
response = requests.get(url)
response_content = response.content
root = ET.fromstring(response_content)
date = root.attrib.get('Date')

Usd = None
for valute in root.findall('Valute'):
    char_code = valute.find('CharCode').text
    if char_code == 'USD':
        Usd = valute.find('Value').text
        Usd = float(Usd.replace(',', '.'))
        break
Eur = None
for valute in root.findall('Valute'):
    char_code = valute.find('CharCode').text
    if char_code == 'EUR':
        Eur = valute.find('Value').text
        Eur = float(Eur.replace(',', '.'))

TOKEN = "7477179769:AAHNFb2RWHD2w_lXDK4OusXaZAvTY3rHlY4"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='html'))
dp = Dispatcher()


# Создание таблицы user_states, если она не существует
def create_table():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_states
                      (user_id INTEGER PRIMARY KEY, state TEXT)''')
    conn.commit()
    conn.close()


# Функция для загрузки состояний из базы данных
def load_states():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_states")
    states = {str(row[0]): row[1] for row in cursor.fetchall()}
    conn.close()
    return states


# Функция для сохранения состояний в базу данных
def save_states(states):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_states")
    for user_id, state in states.items():
        cursor.execute("INSERT INTO user_states (user_id, state) VALUES (?, ?)", (user_id, state))
    conn.commit()
    conn.close()


# Загрузка состояний при старте
create_table()  # Убедимся, что таблица создана перед использованием
user_states = load_states()


def get_user_state(user_id):
    return user_states.get(str(user_id), 'default_state')


def set_user_state(user_id, state):
    user_states[str(user_id)] = state
    save_states(user_states)


states_of_choose = {}

converts = ["RUB -> USD", "RUB -> EUR", "USD -> RUB", "USD -> EUR", "EUR -> USD", 'EUR -> RUB']
builder = ReplyKeyboardBuilder()
builder.button(text="RUB -> USD")
builder.button(text="RUB -> EUR")
builder.button(text="USD -> RUB")
builder.button(text="USD -> EUR")
builder.button(text="EUR -> USD")
builder.button(text="EUR -> RUB")
builder.adjust(2)
builder.resize_keyboard = True


@dp.message(CommandStart())
async def send_welcome(message: Message):
    set_user_state(message.from_user.id, '0')
    await message.answer("Привет, я бот - конвертер валют!")
    await message.answer("К сожалению, наш бота пока поддерживает только 3 валюты, но в будущем мы это исправим!")
    await message.answer(
        "Этот бот поддерживает онлайн-сихронизацию курса валют от ЦБ РФ. Данный курс действителен на " + date)
    await message.answer(text='Выбери, из какой валюты в какую ты будешь конвертировать и введи количество.',
                         reply_markup=builder.as_markup())


@dp.message()
async def conv(message: Message):
    user_id = message.from_user.id
    state = get_user_state(user_id)
    if state == '0' and message.text in converts:
        set_user_state(user_id, '1')
        await message.answer('Теперь введите сумму...')
        states_of_choose[message.from_user.id] = message.text
    elif state == '1':
        set_user_state(user_id, '0')
        if states_of_choose[message.from_user.id] == "RUB -> USD":
            summ = float(message.text) / Usd
            await message.answer("ответ: " + str(round(summ, 2)))
        elif states_of_choose[message.from_user.id] == "RUB -> EUR":
            summ = float(message.text) / Eur
            await message.answer("ответ: " + str(round(summ, 2)))
        elif states_of_choose[message.from_user.id] == "USD -> EUR":
            summ = float(message.text) / 1.07
            await message.answer("ответ: " + str(round(summ, 2)))
        elif states_of_choose[message.from_user.id] == "USD -> RUB":
            summ = float(message.text) * Usd
            await message.answer("ответ: " + str(round(summ, 2)))
        elif states_of_choose[message.from_user.id] == "EUR -> USD":
            summ = float(message.text) * 1.07
            await message.answer("ответ: " + str(round(summ, 2)))
        elif states_of_choose[message.from_user.id] == "EUR -> RUB":
            summ = float(message.text) * Eur
            await message.answer("ответ: " + str(round(summ, 2)))


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    create_table()  # Создаем таблицу при запуске программы
    asyncio.run(main())