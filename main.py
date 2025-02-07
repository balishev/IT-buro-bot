import asyncio
import logging
import sqlite3
import requests
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


##############################################
# Инициализация базы данных пользователей
##############################################
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
        city TEXT,
        university TEXT,
        faculty TEXT,
        group_name TEXT,
        hobbies TEXT,
        future_interests TEXT,
        activity_level INTEGER,
        social_level INTEGER,
        weekly_plans TEXT
    )
    """)
    conn.commit()
    conn.close()


init_db()

##############################################
# Клавиатура выбора языка
##############################################
language_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="English"), KeyboardButton(text="Русский")],
        [KeyboardButton(text="Français"), KeyboardButton(text="Español")],
        [KeyboardButton(text="中文"), KeyboardButton(text="한국어")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


##############################################
# Функция GigaChat (заглушка)
##############################################
def gigachat_find_relevant_events(user_interests, all_events):
    url = "https://api.gigachat.ru/v1/find-events"  # Примерный эндпоинт
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_GIGACHAT_TOKEN"  # Замените на реальный токен
    }
    payload = {
        "user_interests": user_interests,
        "events": all_events
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data.get("description", "Нет поля description в ответе GigaChat.")
        else:
            return f"GigaChat вернул ошибку: {response.status_code}"
    except Exception as e:
        return f"Ошибка при запросе к GigaChat: {e}"


##############################################
# Получить все события из events.db
##############################################
def get_all_events():
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, date, link, short_desc FROM events")
    rows = cursor.fetchall()
    conn.close()

    events_list = []
    for row in rows:
        events_list.append({
            "title": row[0],
            "date": row[1],
            "link": row[2],
            "short_desc": row[3]
        })
    return events_list


##############################################
# /start
##############################################
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    telegram_id = message.from_user.id
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()

    # Если пользователь не в базе, добавим
    if user is None:
        cursor.execute("INSERT INTO users (telegram_id) VALUES (?)", (telegram_id,))
        conn.commit()

    conn.close()
    # Предложим выбрать язык
    await message.answer("Выберите язык:", reply_markup=language_keyboard)


##############################################
# /event
##############################################
@dp.message(Command("event"))
async def event_command_handler(message: types.Message):
    telegram_id = message.from_user.id

    # 1. Получаем профиль пользователя
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        await message.answer("Сначала нужно зарегистрироваться через /start.")
        return

    # Собираем интересы (hobbies + future_interests)
    user_interests = (user[10] or "") + " " + (user[11] or "")
    user_interests = user_interests.strip()
    if not user_interests:
        user_interests = "нет интересов"

    # 2. Забираем все события из локальной БД
    all_events = get_all_events()
    if not all_events:
        await message.answer("В базе нет мероприятий. Попробуйте позже.")
        return

    # 3. Обращаемся к GigaChat
    result_text = gigachat_find_relevant_events(user_interests, all_events)

    # 4. Возвращаем результат пользователю
    await message.answer(result_text)


##############################################
# Обработка прочих сообщений: регистрация
##############################################
@dp.message()
async def process_registration(message: types.Message):
    telegram_id = message.from_user.id
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()

    if user is None:
        # Если почему-то нет записи, игнорируем
        conn.close()
        return

    # user = (
    #   0: id,
    #   1: telegram_id,
    #   2: language,
    #   3: username,
    #   4: password,
    #   5: country,
    #   6: city,
    #   7: university,
    #   8: faculty,
    #   9: group_name,
    #   10: hobbies,
    #   11: future_interests,
    #   12: activity_level,
    #   13: social_level,
    #   14: weekly_plans
    # )
    if user[2] is None:
        # Сохраняем язык
        cursor.execute("UPDATE users SET language = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Введите ваш логин:")
    elif user[3] is None:
        # Сохраняем логин
        cursor.execute("UPDATE users SET username = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Придумайте пароль:")
    elif user[4] is None:
        # Сохраняем пароль
        cursor.execute("UPDATE users SET password = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Выберите страну:")
    elif user[5] is None:
        # Сохраняем страну
        cursor.execute("UPDATE users SET country = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Введите город ВУЗа:")
    elif user[6] is None:
        # Сохраняем город
        cursor.execute("UPDATE users SET city = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Введите название ВУЗа:")
    elif user[7] is None:
        # Сохраняем ВУЗ
        cursor.execute("UPDATE users SET university = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Введите факультет:")
    elif user[8] is None:
        # Сохраняем факультет
        cursor.execute("UPDATE users SET faculty = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Введите название группы:")
    elif user[9] is None:
        # Сохраняем группу
        cursor.execute("UPDATE users SET group_name = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Расскажи немного о своих интересах: Укажи свои хобби")
    elif user[10] is None:
        # Сохраняем хобби
        cursor.execute("UPDATE users SET hobbies = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Что бы тебе хотелось изучить в будущем?")
    elif user[11] is None:
        # Сохраняем будущие интересы
        cursor.execute("UPDATE users SET future_interests = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Оцени, насколько ты активный человек от 1 до 10")
    elif user[12] is None:
        # Сохраняем уровень активности
        cursor.execute("UPDATE users SET activity_level = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Оцени, насколько ты общительный человек от 1 до 10")
    elif user[13] is None:
        # Сохраняем уровень общительности
        cursor.execute("UPDATE users SET social_level = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer(
            "Если у тебя уже есть внеурочные планы на неделе, ты можешь о них написать здесь (в формате: понедельник; 15:00; плаванье)")
    elif user[14] is None:
        # Сохраняем внеурочные планы
        cursor.execute("UPDATE users SET weekly_plans = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Регистрация прошла успешно!")
    else:
        await message.answer("Вы уже зарегистрированы!")

    conn.close()


##############################################
# Точка входа
##############################################
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
