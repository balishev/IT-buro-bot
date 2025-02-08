import logging
import os
import asyncio
import re
import json
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Необходимо указать BOT_TOKEN в файле .env")

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from localization import get_msg, LANG_MAP
from states import Registration, AdditionalInfo, EditingSchedule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Файл для хранения расписаний
SCHEDULES_FILE = "schedules.json"


def load_schedules():
    if os.path.exists(SCHEDULES_FILE):
        with open(SCHEDULES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_schedules(schedules):
    with open(SCHEDULES_FILE, "w", encoding="utf-8") as f:
        json.dump(schedules, f, ensure_ascii=False, indent=4)


user_schedules = load_schedules()

# Глобовые словари для хранения данных
registered_users = set()
user_profiles = {}  # Дополнительная информация


# --- Регистрационный поток ---

@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if user_id in registered_users:
        await message.answer(get_msg("en", "already_registered"), parse_mode="HTML")
        return
    await message.answer(get_msg("en", "greeting"), parse_mode="HTML")
    lang_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Русский", callback_data="lang_ru"),
         InlineKeyboardButton(text="English", callback_data="lang_en")],
        [InlineKeyboardButton(text="Беларускі", callback_data="lang_be"),
         InlineKeyboardButton(text="Қазақша", callback_data="lang_kk")],
        [InlineKeyboardButton(text="中文", callback_data="lang_zh"),
         InlineKeyboardButton(text="한국어", callback_data="lang_ko")]
    ])
    await message.answer("Please choose your language:", reply_markup=lang_kb)
    await state.set_state(Registration.language)


@dp.callback_query(lambda callback: callback.data in LANG_MAP, StateFilter(Registration.language))
async def language_chosen(callback: types.CallbackQuery, state: FSMContext) -> None:
    lang_code = LANG_MAP[callback.data]
    await state.update_data(language=lang_code)
    logger.info(f"User {callback.from_user.id} выбрал язык: {lang_code}")
    await callback.answer()
    await callback.message.answer(get_msg(lang_code, "enter_login"), parse_mode="HTML")
    await state.set_state(Registration.account_login)


@dp.message(StateFilter(Registration.account_login))
async def process_login(message: types.Message, state: FSMContext) -> None:
    login = message.text.strip()
    data = await state.get_data()
    lang = data.get("language", "en")
    if not re.fullmatch(r'^[A-Za-z0-9_]+$', login):
        await message.answer(get_msg(lang, "invalid_login"), parse_mode="HTML")
        return
    await state.update_data(login=login)
    logger.info(f"User {message.from_user.id} ввёл логин: {login}")
    await message.answer(get_msg(lang, "enter_password"), parse_mode="HTML")
    await state.set_state(Registration.account_password)


@dp.message(StateFilter(Registration.account_password))
async def process_password(message: types.Message, state: FSMContext) -> None:
    password = message.text.strip()
    await state.update_data(password=password)
    data = await state.get_data()
    lang = data.get("language", "en")
    logger.info(f"User {message.from_user.id} ввёл пароль.")
    await message.answer(get_msg(lang, "enter_city"), parse_mode="HTML")
    await state.set_state(Registration.city)


@dp.message(StateFilter(Registration.city))
async def process_city(message: types.Message, state: FSMContext) -> None:
    city = message.text.strip()
    await state.update_data(city=city)
    data = await state.get_data()
    lang = data.get("language", "en")
    logger.info(f"User {message.from_user.id} ввёл город: {city}")
    # Переходим к выбору вуза
    uni_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ЦУ", callback_data="uni_cu"),
         InlineKeyboardButton(text="Бауманка", callback_data="uni_bauman")],
        [InlineKeyboardButton(text="ВШЭ", callback_data="uni_hse")]
    ])
    await message.answer(get_msg(lang, "choose_university"), reply_markup=uni_kb, parse_mode="HTML")
    await state.set_state(Registration.university)


@dp.callback_query(lambda callback: callback.data in ["uni_cu", "uni_bauman", "uni_hse"],
                   StateFilter(Registration.university))
async def process_university(callback: types.CallbackQuery, state: FSMContext) -> None:
    global registered_users
    uni_map = {
        "uni_cu": "ЦУ",
        "uni_bauman": "Бауманка",
        "uni_hse": "ВШЭ"
    }
    university = uni_map.get(callback.data, "")
    await state.update_data(university=university)
    data = await state.get_data()
    lang = data.get("language", "en")
    logger.info(f"User {callback.from_user.id} выбрал вуз: {university}")
    await callback.answer()

    # Отправляем сообщение с псевдоссылкой для авторизации в вузе
    await callback.message.answer(get_msg(lang, "university_auth"), parse_mode="HTML")
    await asyncio.sleep(3)

    # Создаем псевдо расписание с красивым форматированием, если его ещё нет
    user_id = callback.from_user.id
    if str(user_id) not in user_schedules:
        user_schedules[str(user_id)] = {
            "ПН": "03.02.2025\n09:00-10:30: Лекция по математике\n10:45-12:15: Семинар по физике\n13:00-14:30: Практическое занятие по программированию",
            "ВТ": "04.02.2025\n09:00-10:30: Лекция по информатике\n10:45-12:15: Практикум по алгоритмам\n13:00-14:30: Лабораторная по сетям",
            "СР": "05.02.2025\n09:00-10:30: Лекция по истории\n10:45-12:15: Семинар по обществознанию\n13:00-14:30: Практическое занятие по праву",
            "ЧТ": "06.02.2025\n09:00-10:30: Лекция по литературе\n10:45-12:15: Практикум по русскому языку\n13:00-14:30: Кафедральная практика",
            "ПТ": "07.02.2025\n09:00-10:30: Лабораторная по химии\n10:45-12:15: Семинар по биологии\n13:00-14:30: Практическое занятие по экологии",
            "СБ": "08.02.2025\n10:00-12:00: Практическая работа в лаборатории\n13:00-14:30: Семинар по спорту\n15:00-16:30: Внеучебная деятельность",
            "ВС": "09.02.2025\nВыходной"
        }
        save_schedules(user_schedules)
    else:
        user_schedules.update(load_schedules())

    # Формируем финальное меню: если дополнительная информация ещё не заполнена – 4 кнопки, иначе – 3
    if str(user_id) not in user_profiles:
        final_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_msg(lang, "event_search"), callback_data="search_events")],
            [InlineKeyboardButton(text=get_msg(lang, "update_info"), callback_data="update_info")],
            [InlineKeyboardButton(text=get_msg(lang, "edit_schedule"), callback_data="edit_schedule")],
            [InlineKeyboardButton(text=get_msg(lang, "view_schedule"), callback_data="view_schedule")]
        ])
    else:
        final_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_msg(lang, "view_schedule"), callback_data="view_schedule")],
            [InlineKeyboardButton(text=get_msg(lang, "edit_schedule"), callback_data="edit_schedule")],
            [InlineKeyboardButton(text=get_msg(lang, "event_search"), callback_data="search_events")]
        ])
    await callback.message.answer(get_msg(lang, "registration_finished"), reply_markup=final_kb, parse_mode="HTML")

    registered_users.add(user_id)
    await state.clear()


# --- Обработка финальных кнопок ---

@dp.callback_query(lambda c: c.data == "search_events")
async def search_events_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.answer("Поиск событий пока не реализован.", show_alert=True)


@dp.callback_query(lambda c: c.data == "edit_schedule")
async def edit_schedule_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(EditingSchedule.new_event)
    await callback.message.answer(get_msg("ru", "edit_schedule_prompt"), parse_mode="HTML")


@dp.message(StateFilter(EditingSchedule.new_event))
async def process_new_event(message: types.Message, state: FSMContext) -> None:
    text = message.text.strip()
    # Ожидаемый формат: [День] [Время начала] - [Время конца] [Событие]
    pattern = r"^(ПН|ВТ|СР|ЧТ|ПТ|СБ|ВС)\s+(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})\s+(.+)$"
    match = re.match(pattern, text)
    if not match:
        await message.answer("Неверный формат. Попробуйте снова. Пример: ПН 19:40 - 21:30 просмотр фильма",
                             parse_mode="HTML")
        return
    day, start, end, event_desc = match.groups()
    event_line = f"{start}-{end}: {event_desc}"
    user_id = str(message.from_user.id)
    schedules = load_schedules()
    user_schedule = schedules.get(user_id, {})
    # Обновляем расписание: записываем только дату и события без повторения дня
    if day not in user_schedule:
        user_schedule[day] = f"{get_date_for_day(day)}\n{event_line}"
    else:
        user_schedule[day] += f"\n{event_line}"
    schedules[user_id] = user_schedule
    save_schedules(schedules)
    global user_schedules
    user_schedules = schedules
    await message.answer("Событие добавлено.", parse_mode="HTML")
    # После обновления информации выводим финальное меню
    final_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_msg("ru", "view_schedule"), callback_data="view_schedule")],
        [InlineKeyboardButton(text=get_msg("ru", "edit_schedule"), callback_data="edit_schedule")],
        [InlineKeyboardButton(text=get_msg("ru", "event_search"), callback_data="search_events")]
    ])
    await message.answer(get_msg("ru", "registration_finished"), reply_markup=final_kb, parse_mode="HTML")
    await state.clear()


@dp.callback_query(lambda c: c.data == "view_schedule")
async def view_schedule_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    days = [("ПН", "ПН"), ("ВТ", "ВТ"), ("СР", "СР"), ("ЧТ", "ЧТ"), ("ПТ", "ПТ"), ("СБ", "СБ"), ("ВС", "ВС")]
    day_kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=abbr, callback_data=f"day_{abbr}")] for abbr, _ in days])
    await callback.answer()
    await callback.message.answer("Выберите день недели:", reply_markup=day_kb, parse_mode="HTML")


@dp.callback_query(lambda c: c.data.startswith("day_"))
async def day_schedule_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    day = callback.data[4:]
    user_id = str(callback.from_user.id)
    schedule = user_schedules.get(user_id, {})
    day_schedule = schedule.get(day, "Расписание не найдено.")
    await callback.answer()
    await callback.message.answer(f"<b>{day}</b>\n{day_schedule}", parse_mode="HTML")


@dp.callback_query(lambda c: c.data == "update_info")
async def update_info_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    # Для обновления информации вопросы будут на русском
    lang = "ru"
    update_activity_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(1, 6)]
    ])
    await state.set_state(AdditionalInfo.activity)
    await callback.message.answer(get_msg(lang, "update_enter_activity"), reply_markup=update_activity_kb,
                                  parse_mode="HTML")


@dp.callback_query(lambda c: c.data in [str(i) for i in range(1, 6)], StateFilter(AdditionalInfo.activity))
async def update_info_activity_cb(callback: types.CallbackQuery, state: FSMContext) -> None:
    chosen_activity = callback.data
    await state.update_data(additional_activity=chosen_activity)
    lang = "ru"
    logger.info(f"User {callback.from_user.id} (update info) выбрал активность: {chosen_activity}")
    await callback.message.delete()
    update_sociability_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(1, 6)]
    ])
    await state.set_state(AdditionalInfo.sociability)
    await bot.send_message(callback.message.chat.id, get_msg(lang, "update_enter_sociability"),
                           reply_markup=update_sociability_kb, parse_mode="HTML")
    await callback.answer()


@dp.callback_query(lambda c: c.data in [str(i) for i in range(1, 6)], StateFilter(AdditionalInfo.sociability))
async def update_info_sociability_cb(callback: types.CallbackQuery, state: FSMContext) -> None:
    chosen_sociability = callback.data
    await state.update_data(additional_sociability=chosen_sociability)
    lang = "ru"
    logger.info(f"User {callback.from_user.id} (update info) выбрал общительность: {chosen_sociability}")
    await callback.message.delete()
    await state.set_state(AdditionalInfo.interests)
    await bot.send_message(callback.message.chat.id, get_msg(lang, "update_enter_hobbies"), parse_mode="HTML")
    await callback.answer()


@dp.message(StateFilter(AdditionalInfo.interests))
async def update_info_interests(message: types.Message, state: FSMContext) -> None:
    interests = message.text.strip()
    await state.update_data(additional_interests=interests)
    lang = "ru"
    user_profiles[str(message.from_user.id)] = {
        "activity": (await state.get_data()).get("additional_activity"),
        "sociability": (await state.get_data()).get("additional_sociability"),
        "interests": interests
    }
    await message.answer(get_msg(lang, "info_updated"), parse_mode="HTML")
    # После обновления информации выводим финальное меню
    final_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_msg(lang, "view_schedule"), callback_data="view_schedule")],
        [InlineKeyboardButton(text=get_msg(lang, "edit_schedule"), callback_data="edit_schedule")],
        [InlineKeyboardButton(text=get_msg(lang, "event_search"), callback_data="search_events")]
    ])
    await message.answer(get_msg(lang, "registration_finished"), reply_markup=final_kb, parse_mode="HTML")
    await state.clear()


if __name__ == '__main__':
    async def main():
        await dp.start_polling(bot)


    asyncio.run(main())
