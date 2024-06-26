import asyncio
import logging
import sys
import sqlite3

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message

TOKEN = "7477179769:AAHNFb2RWHD2w_lXDK4OusXaZAvTY3rHlY4"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='html'))
dp = Dispatcher()

# Подключение к базе данных SQLite
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Создаем таблицу
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    state INTEGER
)
''')
conn.commit()


# команды
@dp.message(CommandStart())
async def send_welcome(message: Message) -> None:
    await message.answer("Привет, я бот Николая!")
    await message.answer("Введите свое имя...")
    user_id = message.from_user.id
    c.execute('''INSERT INTO users (id, state) VALUES (?, 0)''', (user_id,))
    conn.commit()

@dp.message()
async def name(message: Message):
    user_id = message.from_user.id
    name = message.text

    # Получаем текущее состояние пользователя из базы данных
    c.execute('SELECT state FROM users WHERE id = ?', (user_id,))
    current_state = c.fetchone()[0]  # Получаем первую строку результата запроса

    if current_state == 0:
    # Обновляем имя пользователя
        c.execute('UPDATE users SET name = ? WHERE id = ?', (name, user_id))
        conn.commit()

        await message.answer("Ваше имя сохранено как: " + name + '. Вы можете его изменить введя новое.')
async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
