import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
# from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
# from async_cb_rate.parser import get_rate, get_codes, get_all_rates

import xml.etree.ElementTree as ET
import requests

Usd = float(
        ET.fromstring(requests.get("https://www.cbr.ru/scripts/XML_daily.asp").text)
        .find("./Valute[CharCode='USD']/VunitRate")
        .text.replace(",", "."))
Eur = float(
        ET.fromstring(requests.get("https://www.cbr.ru/scripts/XML_daily.asp").text)
        .find("./Valute[CharCode='EUR']/VunitRate")
        .text.replace(",", "."))


TOKEN = "7477179769:AAHNFb2RWHD2w_lXDK4OusXaZAvTY3rHlY4"
# TOKEN = "7416547309:AAGCI248cWXAaTsSnOIob7UdGh9NYIFVTXo"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='html'))
dp = Dispatcher()


states = {}
states_of_choose = {}

Eur = 94.26

converts = ["RUB -> USD", "RUB -> EUR", "USD -> RUB", "USD -> EUR", "EUR -> USD", 'EUR -> RU']
builder = ReplyKeyboardBuilder()
builder.button(text="RUB -> USD")
builder.button(text="RUB -> EUR")
builder.button(text="USD -> RUB")
builder.button(text="USD -> EUR")
builder.button(text="EUR -> USD")
builder.button(text="EUR -> RUB")
builder.adjust(2)
builder.resize_keyboard=True

# команды
@dp.message(CommandStart())
async def send_welcome(message: Message) -> None:
    states[message.from_user.id] = '0'
    await message.answer("Привет, я бот - конвертер валют!")
    await message.answer("К сожалению, наш бота пока поддерживает только 3 валюты, но в будущем мы это исправим!")
    await message.answer(text='Выбери, из какой валюты в какую ты будешь конвертировать и введи количество.',
                         reply_markup=builder.as_markup())

@dp.message()
async def conv(message: Message):
    if states[message.from_user.id] == '0' and message.text in converts:
        states[message.from_user.id] = '1'
        await message.answer('Теперь введите сумму: ')
        states_of_choose[message.from_user.id] = message.text
    elif states[message.from_user.id] == '1':
        states[message.from_user.id] = '0'
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
        elif states_of_choose[message.from_user.id] == "EUR -> RUBssss":
            summ = float(message.text) * Eur
            await message.answer("ответ: " + str(round(summ, 2)))









async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
