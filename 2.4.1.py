#СОЗДАТЬ В ПАПКЕ ПРОЕКТА ФАЙЛ "user_states.json"

import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import json
import os
import xml.etree.ElementTree as ET
import requests

STATE_FILE = 'user_states.json'

url = 'https://www.cbr.ru/scripts/XML_daily.asp'
response = requests.get(url)# Получение XML файла
response_content = response.content
root = ET.fromstring(response_content)# Парсинг XML файла
date = root.attrib.get('Date')#Извлечение атрибута Date из корневого элемента

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
        break

TOKEN = "7477179769:AAHNFb2RWHD2w_lXDK4OusXaZAvTY3rHlY4"
# TOKEN = "7416547309:AAGCI248cWXAaTsSnOIob7UdGh9NYIFVTXo"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='html'))
dp = Dispatcher()

# Функция для загрузки состояний из файла
def load_states():
    if not os.path.exists(STATE_FILE):
        # Создание пустого файла, если он не существует
        with open(STATE_FILE, 'w') as f:
            json.dump({}, f)

    with open(STATE_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

# Функция для сохранения состояний в файл
def save_states(states):
    with open(STATE_FILE, 'w') as f:
        json.dump(states, f, indent=4)

# Загрузка состояний при старте
user_states = load_states()


def get_user_state(user_id):
    return user_states.get(str(user_id), 'default_state')

# Функция для установки состояния пользователя
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


# команды
@dp.message(CommandStart())
async def send_welcome(message: Message) -> None:
    set_user_state(message.from_user.id, '0')
    await message.answer("Привет, я бот - конвертер валют!")
    await message.answer("К сожалению, наш бота пока поддерживает только 3 валюты, но в будущем мы это исправим!")
    await message.answer("Этот бот поддерживает онлайн-сихронизацию курса валют от ЦБ РФ. Данный курс действителен на " + date)
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


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
