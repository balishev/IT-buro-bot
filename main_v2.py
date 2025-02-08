"""Full-featured Telegram Bot MVP, adapted for Aiogram 3.x >= 3.7.0, storing user profiles in SQLite.
Now includes:
1) User city in registration,
2) Real GigaChat-based translation via AI_API_KEY.
"""

import os
import logging
import asyncio
import requests
from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import datetime
import aiosqlite
import aiohttp
from dotenv import load_dotenv
from datetime import datetime, timedelta
###############################
# Aiogram 3.7+ Bot initialization changes
###############################
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import Bot, DefaultBotProperties
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat

###############################
# Load environment variables
###############################
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AI_API_KEY = os.getenv("AI_API_KEY")  # For GigaChat usage
DATABASE_PATH = os.getenv("DATABASE_PATH", "bot_database.db")

###############################
# Configure logging
###############################
logging.basicConfig(level=logging.INFO)

###############################
# Create Bot with parse_mode in DefaultBotProperties
###############################
session = AiohttpSession()
bot = Bot(
    token=TELEGRAM_TOKEN,
    session=session,
    default=DefaultBotProperties(parse_mode="HTML")
)


def get_upcoming_events(city='msk', days_ahead=30, max_events=30):
    # Базовый URL API KudaGo
    base_url = "https://kudago.com/public-api/v1.4/events/"

    # Параметры запроса
    params = {
        'location': city,
        'actual_since': int(datetime.now().timestamp()),
        'actual_until': int((datetime.now() + timedelta(days=days_ahead)).timestamp()),
        'page_size': max_events,
        'lang': 'ru',
        'fields': 'id,title,dates,place,location,is_free,price,site_url',
        'expand': 'dates,place'
    }

    # Отправка GET-запроса
    response = requests.get(base_url, params=params)

    # Проверка успешности запроса
    if response.status_code == 200:
        events = response.json().get('results', [])
        ev_lst = []
        for event in events:
            '''print(f"Название: {event['title']}")
            print(f"Дата: {event['dates'][0]['start']}")
            print(f"Место: {event['place']['title'] if event['place'] else 'Не указано'}")
            print(f"Стоимость: {'Бесплатно' if event['is_free'] else event.get('price', 'Не указана')}")
            print(f"Ссылка: {event['site_url']}")
            print("-" * 40)'''
            ev_lst.append(event['title'])
    else:
        print(f"Ошибка при запросе данных: {response.status_code}")
        return []


# Пример использования функции


def suggest(interests, events):
    # print('start')
    load_dotenv()
    credentials = os.getenv("GIGACHAT_CREDENTIALS", "")
    # Авторизация в GigaChat
    model = GigaChat(
        credentials=credentials,
        scope="GIGACHAT_API_PERS",
        model="GigaChat",
        # Отключает проверку наличия сертификатов НУЦ Минцифры
        verify_ssl_certs=False,
    )

    messages = [
        SystemMessage(
            content=f"Ты бот, который помогает иностранному студенту ассимилироваться в России, из предложеного списка мероприятий предложи студенту мероприятия на основе его интересов: {interests}:"
        )
    ]
    # print('1')
    messages.append(HumanMessage(content=str(events)))
    res = model.invoke(messages)
    messages.append(res)
    return res.content


async def gigachat_translate(text: str, target_language: str = "ru") -> str:
    load_dotenv()
    credentials = os.getenv("GIGACHAT_CREDENTIALS", "")
    # Авторизация в GigaChat
    model = GigaChat(
        credentials=credentials,
        scope="GIGACHAT_API_PERS",
        model="GigaChat",
        # Отключает проверку наличия сертификатов НУЦ Минцифры
        verify_ssl_certs=False,
    )

    messages = [
        SystemMessage(
            content=f"Ты бот-переводчик, переведи текст на язык {target_language}:"
        )
    ]

    messages.append(HumanMessage(content=text))
    res = model.invoke(messages)
    messages.append(res)
    return res.content


async def init_db():
    """Initialize the SQLite database (and do migrations if needed)."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Users table with 'city' column
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                name TEXT,
                country TEXT,
                city TEXT,
                interests TEXT,
                language_level TEXT,
                is_mentor INTEGER DEFAULT 0
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                tags TEXT,
                date TEXT
            )
        ''')
        # Insert some demo events if table is empty
        cursor = await db.execute("SELECT COUNT(*) FROM events")
        count = (await cursor.fetchone())[0]
        if count == 0:
            sample_events = [
                ("City Tour", "Explore the main city attractions.", "tour,city,sightseeing", "2025-03-10"),
                ("Language Exchange", "Practice languages with locals.", "language,exchange,communication",
                 "2025-03-11"),
                ("Music Festival", "Enjoy live music performances.", "music,festival,concert", "2025-03-12"),
                (
                    "Russian Culture 101", "Intro session on local traditions.", "culture,traditions,lecture",
                    "2025-03-15")
            ]
            await db.executemany(
                "INSERT INTO events (title, description, tags, date) VALUES (?,?,?,?)",
                sample_events
            )
            await db.commit()

        # Optional: If we want to add new columns in the future, we could do migrations here.

        await db.commit()


###############################
# FSM States
###############################
class RegistrationState(StatesGroup):
    waiting_for_name = State()
    waiting_for_country = State()
    waiting_for_city = State()
    waiting_for_interests = State()
    waiting_for_language = State()


###############################
# Create Dispatcher & Router
###############################
from aiogram import Router

router = Router()


###############################
# /start handler
###############################
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    # Clear any previous state
    await state.clear()

    # Check if user is already in DB
    user_id = message.from_user.id
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT * FROM users WHERE telegram_id=?", (user_id,))
        exists = await cursor.fetchone()

    if exists:
        await message.answer(
            "Welcome back! You are already registered.\n"
            "Use /events to see upcoming events, /mentor to request a mentor, or /help for more info.")
    else:
        await message.answer("Hello! Let's register you. What's your name?")
        await state.set_state(RegistrationState.waiting_for_name)


@router.message(RegistrationState.waiting_for_name, F.content_type == ContentType.TEXT)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("What country are you from?")
    await state.set_state(RegistrationState.waiting_for_country)


@router.message(RegistrationState.waiting_for_country, F.content_type == ContentType.TEXT)
async def process_country(message: Message, state: FSMContext):
    await state.update_data(country=message.text.strip())
    await message.answer("In which city do you live?")
    await state.set_state(RegistrationState.waiting_for_city)


@router.message(RegistrationState.waiting_for_city, F.content_type == ContentType.TEXT)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text.strip())
    await message.answer("What are your interests? (e.g. music, sports, culture)")
    await state.set_state(RegistrationState.waiting_for_interests)


@router.message(RegistrationState.waiting_for_interests, F.content_type == ContentType.TEXT)
async def process_interests(message: Message, state: FSMContext):
    await state.update_data(interests=message.text.strip())
    await message.answer("What is your language level? (e.g. A1, B2, C1)")
    await state.set_state(RegistrationState.waiting_for_language)


@router.message(RegistrationState.waiting_for_language, F.content_type == ContentType.TEXT)
async def process_language(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_data["language_level"] = message.text.strip()

    user_id = message.from_user.id
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO users (telegram_id, name, country, city, interests, language_level) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                user_id,
                user_data["name"],
                user_data["country"],
                user_data["city"],
                user_data["interests"],
                user_data["language_level"]
            )
        )
        await db.commit()

    await message.answer(
        "Registration complete!\n"
        "Use /events to see upcoming events.\n"
        "Use /mentor to request a mentor.\n"
        "Use /help for more options.")

    await state.clear()


###############################
# /help handler
###############################
@router.message(Command(commands=["help"]))
async def cmd_help(message: Message):
    help_text = (
        "Here are some commands you can use:\n"
        "/start - Start or reset the bot (registration)\n"
        "/events - Get event recommendations\n"
        "/mentor - Request a mentor\n"
        "/translate &lt;text&gt; - Translate text (via GigaChat)\n"
        "/phrase &lt;topic&gt; - Get useful phrases\n"
        "/help - Show this help message"
    )
    await message.answer(help_text)


###############################
# /events handler
###############################
@router.message(Command(commands=["events"]))
async def cmd_events(message: Message):
    user_id = message.from_user.id
    # Retrieve user interests
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT interests, city FROM users WHERE telegram_id=?", (user_id,))
        row = await cursor.fetchone()
        if not row:
            await message.answer("You are not registered yet. Please use /start.")
            return
        user_interests, user_city = row[0], row[1]
        events = get_upcoming_events()

        txt = suggest(user_interests, events)
        print(txt)
        await message.answer(txt)
        '''# For simplicity, naive match on event tags.
        # In the future, we can parse city-based events. For now, we ignore city.
        all_events = []
        cursor = await db.execute("SELECT id, title, description, tags, date FROM events")
        events_data = await cursor.fetchall()
        for e_id, title, desc, tags, date_ in events_data:
            if user_interests:
                u_tags = [t.strip().lower() for t in user_interests.split(",")]
                e_tags = [t.strip().lower() for t in tags.split(",")] if tags else []
                # If any overlap, consider recommended
                if any(tag in e_tags for tag in u_tags):
                    all_events.append((title, desc, date_))
            else:
                # If user has no interests, show all
                all_events.append((title, desc, date_))

    if not all_events:
        await message.answer("No matching events found for your interests!")
        return

    response_lines = ["Here are some recommended events:"]
    for idx, (title, desc, date_) in enumerate(all_events, start=1):
        response_lines.append(f"\n{idx}) {title}\nDate: {date_}\nDescription: {desc}")
    await message.answer("\n".join(response_lines))'''


###############################
# /mentor handler
###############################
@router.message(Command(commands=["mentor"]))
async def cmd_mentor(message: Message):
    user_id = message.from_user.id
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Check if the user is registered
        cursor = await db.execute("SELECT name FROM users WHERE telegram_id=?", (user_id,))
        row = await cursor.fetchone()
        if not row:
            await message.answer("You are not registered. Please use /start.")
            return

        # For simplicity, pick a random mentor
        cursor_mentor = await db.execute(
            "SELECT telegram_id, name FROM users WHERE is_mentor=1 ORDER BY RANDOM() LIMIT 1")
        mentor_row = await cursor_mentor.fetchone()
        if not mentor_row:
            await message.answer("No mentors available at the moment.")
            return
        mentor_id, mentor_name = mentor_row

    await message.answer(f"We found a mentor: {mentor_name}. They will contact you soon!")


###############################
# /translate handler
###############################
@router.message(Command(commands=["translate"]))
async def cmd_translate(message: Message):
    # Usage: /translate Hello World
    text_parts = message.text.split(maxsplit=1)
    if len(text_parts) < 2:
        await message.answer("Please provide text to translate. Example: /translate Hello")
        return
    to_translate = text_parts[1]

    if not AI_API_KEY:
        await message.answer(
            "[ERROR] AI_API_KEY not set. Cannot perform real translation.\n"
            f"Placeholder translation for: {to_translate}"
        )
        return

    # Attempt real GigaChat translation
    translated_text = await gigachat_translate(to_translate)
    await message.answer(f"Translated to Russian:\n{translated_text}")


###############################
# /phrase handler
###############################
@router.message(Command(commands=["phrase"]))
async def cmd_phrase(message: Message):
    text_parts = message.text.split(maxsplit=1)
    if len(text_parts) < 2:
        await message.answer("Please provide a topic. Example: /phrase shop")
        return
    topic = text_parts[1].lower().strip()

    PHRASE_LIBRARY = {
        "shop": [
            "Я хочу купить... (I want to buy...)",
            "Сколько это стоит? (How much does it cost?)",
            "У вас есть скидки? (Do you have any discounts?)"
        ],
        "cafe": [
            "Можно мне меню? (Can I have a menu?)",
            "Я вегетарианец (I'm a vegetarian)",
            "Счёт, пожалуйста (Check, please)"
        ]
    }

    if topic in PHRASE_LIBRARY:
        lines = PHRASE_LIBRARY[topic]
        text_out = f"Useful phrases for '{topic}':\n\n" + "\n".join(lines)
    else:
        text_out = f"No pre-defined phrases for '{topic}'."
    await message.answer(text_out)


###############################
# Startup event
###############################
@router.startup()
async def on_startup(dispatcher: Dispatcher, bot: Bot):
    logging.info("Bot is starting up. Initializing DB...")
    await init_db()


###############################
# Main entry point
###############################
async def main():
    # Create dispatcher, attach router
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    # Start polling
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
