import asyncio
import logging
import sqlite3
import os
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv


try:
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_gigachat.chat_models import GigaChat
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GIGACHAT_TOKEN = os.getenv("GIGACHAT_TOKEN")  # токен для GigaChat

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
# (А) Функция GigaChat (REST) — старый вариант
##############################################
def gigachat_find_relevant_events_rest(user_interests, all_events):
    """
    Пример REST-запроса к GigaChat на URL:
    https://api.aicloud.sbercloud.ru/publicapi/gigachat/v1/completions
    (или другой, взятый из документации).

    Параметры:
    - user_interests: строка с интересами
    - all_events: список словарей [{title, date, link, short_desc}, ...]

    Возвращает строку-ответ, полученную от GigaChat
    """
    if not GIGACHAT_TOKEN:
        return "Ошибка: нет GIGACHAT_TOKEN в .env"

    url = "https://api.aicloud.sbercloud.ru/publicapi/gigachat/v1/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GIGACHAT_TOKEN}"
    }

    # Генерируем prompt
    prompt_text = (
        f"Интересы пользователя: {user_interests}\n\n"
        f"Список мероприятий: {all_events}\n\n"
        "Подбери самые релевантные и обоснуй выбор."
    )

    payload = {
        "prompt": prompt_text,
        "max_tokens": 500
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("text", "Нет поля text")
            else:
                return "GigaChat не вернул choices"
        else:
            return f"GigaChat вернул ошибку: {response.status_code}"
    except Exception as e:
        return f"Ошибка при запросе к GigaChat (REST): {e}"

##############################################
# (Б) Функция GigaChat через langchain_gigachat
##############################################
def gigachat_find_relevant_events_langchain(user_interests, all_events):
    """
    Пример обращения к GigaChat с помощью langchain-gigachat:
    https://github.com/ai-forever/langchain-gigachat/tree/master/libs/gigachat

    Параметры:
    - user_interests: строка с интересами
    - all_events: список словарей [{title, date, link, short_desc}, ...]

    Возвращает строку-ответ (res.content) от GigaChat.
    """
    if not LANGCHAIN_AVAILABLE:
        return "langchain-gigachat не установлен, используйте REST-вариант."

    if not GIGACHAT_TOKEN:
        return "Ошибка: нет GIGACHAT_TOKEN в .env"

    # Инициализация модели
    # Обратите внимание: 'scope' и 'model' зависят от конфигурации
    model = GigaChat(
        credentials=GIGACHAT_TOKEN,
        scope="GIGACHAT_API_PERS",  # или другой scope
        model="GigaChat",
        verify_ssl_certs=False  # При необходимости
    )

    # Придумайте role/system, как в примере
    system_message = SystemMessage(content="Ты бот, который рекомендует мероприятия.")

    # Формируем контекст
    # all_events в виде строки
    events_str = "\n".join(
        f"- {ev['title']} (дата: {ev['date']}), {ev['short_desc']}, ссылка: {ev['link']}"
        for ev in all_events
    )
    user_prompt = (
        f"Мои интересы: {user_interests}\n\nВот список мероприятий:\n{events_str}\n\n"
        "Помоги подобрать подходящие мероприятия и объясни выбор."
    )

    # Создаем массив сообщений
    messages = [
        system_message,
        HumanMessage(content=user_prompt)
    ]

    # Делаем вызов
    res = model.invoke(messages)
    return res.content  # res.content содержит ответ от GigaChat

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

    if user is None:
        cursor.execute("INSERT INTO users (telegram_id) VALUES (?)", (telegram_id,))
        conn.commit()

    conn.close()
    await message.answer("Выберите язык:", reply_markup=language_keyboard)

##############################################
# /event - получаем релевантные мероприятия
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

    # Интересы
    user_interests = (user[10] or "") + " " + (user[11] or "")
    user_interests = user_interests.strip()
    if not user_interests:
        user_interests = "нет интересов"

    # 2. Все события
    all_events = get_all_events()
    if not all_events:
        await message.answer("В базе нет мероприятий. Попробуйте позже.")
        return

    # 3. Вызов GigaChat (выберите А или Б)

    # (А) Старый вариант (REST):
    # result_text = gigachat_find_relevant_events_rest(user_interests, all_events)

    # (Б) Новый вариант (через langchain_gigachat):
    result_text = gigachat_find_relevant_events_langchain(user_interests, all_events)

    # 4. Выводим результат
    await message.answer(result_text)

##############################################
# Остальные сообщения - логика регистрации
##############################################
@dp.message()
async def process_registration(message: types.Message):
    telegram_id = message.from_user.id
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()

    if user is None:
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
        cursor.execute("UPDATE users SET language = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Введите ваш логин:")
    elif user[3] is None:
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
        await message.answer("Введите город ВУЗа:")
    elif user[6] is None:
        cursor.execute("UPDATE users SET city = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Введите название ВУЗа:")
    elif user[7] is None:
        cursor.execute("UPDATE users SET university = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Введите факультет:")
    elif user[8] is None:
        cursor.execute("UPDATE users SET faculty = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Введите название группы:")
    elif user[9] is None:
        cursor.execute("UPDATE users SET group_name = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Расскажи немного о своих интересах: Укажи свои хобби")
    elif user[10] is None:
        cursor.execute("UPDATE users SET hobbies = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Что бы тебе хотелось изучить в будущем?")
    elif user[11] is None:
        cursor.execute("UPDATE users SET future_interests = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Оцени, насколько ты активный человек от 1 до 10")
    elif user[12] is None:
        cursor.execute("UPDATE users SET activity_level = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Оцени, насколько ты общительный человек от 1 до 10")
    elif user[13] is None:
        cursor.execute("UPDATE users SET social_level = ? WHERE telegram_id = ?", (message.text, telegram_id))
        conn.commit()
        await message.answer("Если у тебя уже есть внеурочные планы на неделе, ты можешь о них написать здесь (в формате: понедельник; 15:00; плаванье)")
    elif user[14] is None:
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
