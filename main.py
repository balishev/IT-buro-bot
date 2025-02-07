import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        language TEXT,
        username TEXT,
        password TEXT,
        country TEXT,
        university TEXT,
        faculty TEXT,
        group_name TEXT
    )
    """)
    conn.commit()
    conn.close()


init_db()

# Клавиатура выбора языка
language_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="English"), KeyboardButton(text="Русский")],
    [KeyboardButton(text="Français"), KeyboardButton(text="Español")],
    [KeyboardButton(text="中文"), KeyboardButton(text="한국어")]
], resize_keyboard=True, one_time_keyboard=True)


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    telegram_id = message.from_user.id
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()
    if user is None:
        cursor.execute("INSERT INTO users (telegram_id) VALUES (?)", (telegram_id,))
        conn.commit()
    conn.close()
    await message.answer("Выберите язык:", reply_markup=language_keyboard)


@dp.message()
async def process_registration(message: types.Message):
    telegram_id = message.from_user.id
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()

    if user is None:
        return

    if user[3] is None:
        cursor.execute("UPDATE users SET username = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Придумайте пароль:")
    elif user[4] is None:
        cursor.execute("UPDATE users SET password = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Выберите страну:")
    elif user[5] is None:
        cursor.execute("UPDATE users SET country = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Введите название ВУЗа:")
    elif user[6] is None:
        cursor.execute("UPDATE users SET university = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Введите факультет:")
    elif user[7] is None:
        cursor.execute("UPDATE users SET faculty = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Введите название группы:")
    elif user[8] is None:
        cursor.execute("UPDATE users SET group_name = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Регистрация прошла успешно!")
    else:
        await message.answer("Вы уже зарегистрированы!")

    conn.close()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
